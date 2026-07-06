from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, crud, models, schemas, services
from app.config import settings
from app.database import get_database

router = APIRouter()


def _seconds_until(value: datetime) -> int:
    now = datetime.now(UTC)
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return max(0, int((value - now).total_seconds()))


async def _store_and_send_otp(
    database: AsyncSession,
    *,
    email: str,
    purpose: str,
    payload: dict,
    enforce_resend_wait: bool = False,
) -> schemas.OTPResponse:
    existing = await crud.latest_otp(database, email, purpose)
    if enforce_resend_wait and existing and _seconds_until(existing.resend_at) > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {_seconds_until(existing.resend_at)} seconds before requesting another code.",
        )

    code = auth.generate_otp()
    record = await crud.create_otp(
        database,
        email=email,
        purpose=purpose,
        code_hash=auth.otp_hash(email, purpose, code),
        payload=payload,
        expires_seconds=settings.otp_expire_seconds,
        resend_seconds=settings.otp_resend_seconds,
    )
    try:
        await auth.send_otp_email(email, code, purpose)
    except HTTPException:
        await crud.mark_otp_consumed(database, record)
        raise
    return schemas.OTPResponse(message="Verification code sent.", email=email)


async def _verified_otp(
    database: AsyncSession,
    *,
    email: str,
    purpose: str,
    code: str,
) -> models.EmailOTP:
    record = await crud.latest_otp(database, email, purpose)
    if record is None:
        raise HTTPException(status_code=400, detail="No active verification code was found.")
    if _seconds_until(record.expires_at) == 0:
        await crud.mark_otp_consumed(database, record)
        raise HTTPException(status_code=400, detail="The verification code has expired.")
    if record.attempts >= settings.otp_max_attempts:
        await crud.mark_otp_consumed(database, record)
        raise HTTPException(status_code=400, detail="Too many incorrect attempts. Request a new code.")
    if not auth.verify_otp_hash(email, purpose, code, record.code_hash):
        await crud.increment_otp_attempts(database, record)
        raise HTTPException(status_code=400, detail="Incorrect verification code.")
    await crud.mark_otp_consumed(database, record)
    return record


@router.post("/auth/register/send-otp", response_model=schemas.OTPResponse)
async def register_send_otp(data: schemas.UserCreate, database: AsyncSession = Depends(get_database)):
    if await crud.get_user_by_email(database, data.email):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    payload = data.model_dump(mode="json", exclude={"password"})
    payload["password_hash"] = auth.hash_password(data.password)
    return await _store_and_send_otp(
        database,
        email=str(data.email).lower(),
        purpose="REGISTER",
        payload=payload,
        enforce_resend_wait=True,
    )


@router.post("/auth/register/resend-otp", response_model=schemas.OTPResponse)
async def register_resend_otp(data: schemas.ForgotPasswordRequest, database: AsyncSession = Depends(get_database)):
    existing = await crud.latest_otp(database, str(data.email), "REGISTER")
    if existing is None:
        raise HTTPException(status_code=400, detail="Start registration again before requesting another code.")
    return await _store_and_send_otp(
        database,
        email=str(data.email).lower(),
        purpose="REGISTER",
        payload=existing.payload,
        enforce_resend_wait=True,
    )


@router.post("/auth/register/verify-otp", response_model=schemas.AuthResponse, status_code=201)
async def register_verify_otp(data: schemas.OTPVerify, database: AsyncSession = Depends(get_database)):
    if await crud.get_user_by_email(database, str(data.email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    record = await _verified_otp(database, email=str(data.email), purpose="REGISTER", code=data.otp)
    payload = record.payload
    user_data = schemas.UserCreate(
        name=payload["name"],
        email=payload["email"],
        password="temporary-password-placeholder",
        country=payload.get("country"),
        phone=payload.get("phone"),
    )
    try:
        user = await crud.create_user(database, user_data, payload["password_hash"])
    except IntegrityError as exc:
        await database.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc
    return schemas.AuthResponse(access_token=auth.create_access_token(user), user=user)


# Kept as a clear migration error for old clients instead of silently creating unverified accounts.
@router.post("/auth/register", status_code=410)
async def legacy_register():
    raise HTTPException(status_code=410, detail="Email verification is required. Use /auth/register/send-otp.")


@router.post("/auth/login", response_model=schemas.AuthResponse)
async def login(data: schemas.UserLogin, database: AsyncSession = Depends(get_database)):
    user = await crud.get_user_by_email(database, data.email)
    if user is None or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Verify your email before signing in.")
    return schemas.AuthResponse(access_token=auth.create_access_token(user), user=user)


@router.post("/auth/forgot-password/send-otp", response_model=schemas.OTPResponse)
async def forgot_password_send(data: schemas.ForgotPasswordRequest, database: AsyncSession = Depends(get_database)):
    user = await crud.get_user_by_email(database, str(data.email))
    if user is not None:
        return await _store_and_send_otp(
            database,
            email=user.email,
            purpose="PASSWORD_RESET",
            payload={"user_id": str(user.id)},
            enforce_resend_wait=True,
        )
    return schemas.OTPResponse(message="If the account exists, a verification code was sent.", email=data.email)


@router.post("/auth/forgot-password/resend-otp", response_model=schemas.OTPResponse)
async def forgot_password_resend(data: schemas.ForgotPasswordRequest, database: AsyncSession = Depends(get_database)):
    user = await crud.get_user_by_email(database, str(data.email))
    if user is not None:
        return await _store_and_send_otp(
            database,
            email=user.email,
            purpose="PASSWORD_RESET",
            payload={"user_id": str(user.id)},
            enforce_resend_wait=True,
        )
    return schemas.OTPResponse(message="If the account exists, a verification code was sent.", email=data.email)


@router.post("/auth/forgot-password/verify-otp", response_model=schemas.PasswordResetToken)
async def forgot_password_verify(data: schemas.OTPVerify, database: AsyncSession = Depends(get_database)):
    record = await _verified_otp(database, email=str(data.email), purpose="PASSWORD_RESET", code=data.otp)
    user = await crud.get_user(database, uuid.UUID(record.payload["user_id"]))
    if user is None:
        raise HTTPException(status_code=400, detail="The account no longer exists.")
    return schemas.PasswordResetToken(reset_token=auth.create_reset_token(user))


@router.post("/auth/forgot-password/reset")
async def forgot_password_reset(data: schemas.PasswordReset, database: AsyncSession = Depends(get_database)):
    user_id = auth.decode_reset_token(data.reset_token)
    user = await crud.get_user(database, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Account not found.")
    await crud.update_user_password(database, user, auth.hash_password(data.new_password))
    return {"message": "Password updated. You can now sign in."}


@router.get("/auth/me", response_model=schemas.UserResponse)
async def me(user: models.User = Depends(auth.get_current_user)):
    return user


@router.patch("/auth/me", response_model=schemas.UserResponse)
async def update_me(
    data: schemas.UserUpdate,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    return await crud.update_user(database, user, data)


@router.post("/auth/password/change")
async def change_password(
    data: schemas.PasswordChange,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    if not auth.verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="The old password is incorrect.")
    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="The new password must be different.")
    await crud.update_user_password(database, user, auth.hash_password(data.new_password))
    return {"message": "Password changed successfully."}


@router.post("/auth/email-change/send-otp", response_model=schemas.OTPResponse)
async def email_change_send(
    data: schemas.EmailChangeRequest,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    if str(data.new_email).lower() == user.email.lower():
        raise HTTPException(status_code=400, detail="This is already your account email.")
    if await crud.get_user_by_email(database, str(data.new_email)):
        raise HTTPException(status_code=409, detail="This email is already used by another account.")
    return await _store_and_send_otp(
        database,
        email=str(data.new_email).lower(),
        purpose="EMAIL_CHANGE",
        payload={"user_id": str(user.id)},
        enforce_resend_wait=True,
    )


@router.post("/auth/email-change/resend-otp", response_model=schemas.OTPResponse)
async def email_change_resend(
    data: schemas.EmailChangeRequest,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    return await _store_and_send_otp(
        database,
        email=str(data.new_email).lower(),
        purpose="EMAIL_CHANGE",
        payload={"user_id": str(user.id)},
        enforce_resend_wait=True,
    )


@router.post("/auth/email-change/verify-otp", response_model=schemas.AuthResponse)
async def email_change_verify(
    data: schemas.EmailChangeVerify,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    if await crud.get_user_by_email(database, str(data.new_email)):
        raise HTTPException(status_code=409, detail="This email is already used by another account.")
    record = await _verified_otp(database, email=str(data.new_email), purpose="EMAIL_CHANGE", code=data.otp)
    if record.payload.get("user_id") != str(user.id):
        raise HTTPException(status_code=403, detail="This verification request belongs to another account.")
    updated = await crud.update_user_email(database, user, str(data.new_email))
    return schemas.AuthResponse(access_token=auth.create_access_token(updated), user=updated)


@router.get("/products/search", response_model=list[schemas.ProductSummary])
async def products_search(q: str = Query(default="", max_length=120), database: AsyncSession = Depends(get_database)):
    return await services.search_products(database, q)


@router.get("/products/{product_id}", response_model=schemas.ProductResponse)
async def product_detail(product_id: uuid.UUID, database: AsyncSession = Depends(get_database)):
    product = await crud.get_product(database, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


@router.post("/products", response_model=schemas.ProductResponse, status_code=201)
async def create_product(
    data: schemas.ProductCreate,
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
    try:
        product = await crud.create_product(database, data)
    except IntegrityError as exc:
        await database.rollback()
        raise HTTPException(status_code=409, detail="The barcode is already assigned to another product.") from exc
    if product.ingredient_text or product.nutrition_data:
        product = await services.refresh_product_assessment(database, product)
    return await crud.get_product(database, product.id)


@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    data: schemas.ProductUpdate,
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
    product = await crud.get_product(database, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    product = await crud.update_product(database, product, data)
    if product.ingredient_text or product.nutrition_data:
        product = await services.refresh_product_assessment(database, product)
    return product


@router.get("/ingredients", response_model=list[schemas.IngredientResponse])
async def ingredients(q: str = Query(default="", max_length=120), database: AsyncSession = Depends(get_database)):
    return await crud.list_ingredients(database, q)


@router.post("/analyze/ingredients", response_model=schemas.AnalysisResponse)
async def analyze_ingredients(
    data: schemas.IngredientCheckRequest,
    user: models.User | None = Depends(auth.get_optional_user),
    database: AsyncSession = Depends(get_database),
):
    return await services.build_analysis(
        database,
        ingredient_text=data.ingredient_text,
        nutrition_data=data.nutrition_data,
        input_type="INGREDIENT_TEXT",
        input_value=data.product_name,
        user=user,
        extracted_text=data.ingredient_text,
    )


@router.post("/scan/code", response_model=schemas.AnalysisResponse)
async def scan_code(
    data: schemas.CodeScanRequest,
    user: models.User | None = Depends(auth.get_optional_user),
    database: AsyncSession = Depends(get_database),
):
    return await services.analyze_code(database, data, user)


@router.post("/scan/image", response_model=schemas.AnalysisResponse)
async def scan_image(
    image: UploadFile = File(...),
    user: models.User | None = Depends(auth.get_optional_user),
    database: AsyncSession = Depends(get_database),
):
    return await services.analyze_image(database, image, user)


@router.get("/scans/{scan_id}", response_model=schemas.AnalysisResponse)
async def scan_result(scan_id: uuid.UUID, database: AsyncSession = Depends(get_database)):
    scan = await crud.get_scan(database, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan result not found.")
    return services.scan_from_model(scan)


@router.get("/history", response_model=list[schemas.ScanHistoryItem])
async def history(user: models.User = Depends(auth.get_current_user), database: AsyncSession = Depends(get_database)):
    scans = await crud.get_history(database, user.id)
    return [
        schemas.ScanHistoryItem(
            id=scan.id,
            input_type=scan.input_type,
            product=scan.product,
            halal_status=scan.halal_status,
            halal_confidence=scan.halal_confidence,
            health_status=scan.health_status,
            health_score=scan.health_score,
            created_at=scan.created_at,
        )
        for scan in scans
    ]


@router.delete("/history/{scan_id}", status_code=204)
async def remove_history(
    scan_id: uuid.UUID,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    if not await crud.delete_scan(database, scan_id, user.id):
        raise HTTPException(status_code=404, detail="Scan not found.")


@router.get("/favorites", response_model=list[schemas.ProductSummary])
async def favorites(user: models.User = Depends(auth.get_current_user), database: AsyncSession = Depends(get_database)):
    return [favorite.product for favorite in await crud.get_favorites(database, user.id)]


@router.post("/favorites/{product_id}", status_code=201)
async def add_favorite(
    product_id: uuid.UUID,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    if await crud.get_product(database, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    favorite = await crud.add_favorite(database, user.id, product_id)
    return {"id": str(favorite.id), "message": "Product saved."}


@router.delete("/favorites/{product_id}", status_code=204)
async def remove_favorite(
    product_id: uuid.UUID,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    await crud.remove_favorite(database, user.id, product_id)


@router.post("/reports", response_model=schemas.ReportResponse, status_code=201)
async def create_report(
    data: schemas.ReportCreate,
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
    report = await crud.create_report(database, user.id, data)
    try:
        await auth.send_contact_notification(user, data.subject, data.category, data.message)
    except HTTPException:
        # The report is safely stored even if optional email notification fails.
        pass
    return report


@router.get("/admin/dashboard", response_model=schemas.AdminDashboard)
async def admin_dashboard(_: models.User = Depends(auth.get_admin_user), database: AsyncSession = Depends(get_database)):
    return await crud.dashboard_counts(database)


@router.post("/admin/ingredients", response_model=schemas.IngredientResponse, status_code=201)
async def admin_create_ingredient(
    data: schemas.IngredientCreate,
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
    try:
        return await crud.create_ingredient(database, data)
    except IntegrityError as exc:
        await database.rollback()
        raise HTTPException(status_code=409, detail="Ingredient name or E-number already exists.") from exc


@router.put("/admin/ingredients/{ingredient_id}", response_model=schemas.IngredientResponse)
async def admin_update_ingredient(
    ingredient_id: uuid.UUID,
    data: schemas.IngredientUpdate,
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
    ingredient = await crud.get_ingredient(database, ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found.")
    return await crud.update_ingredient(database, ingredient, data)


@router.get("/admin/certifications", response_model=list[schemas.CertificationResponse])
async def admin_certifications(_: models.User = Depends(auth.get_admin_user), database: AsyncSession = Depends(get_database)):
    return await crud.list_certifications(database)


@router.post("/admin/certifications", response_model=schemas.CertificationResponse, status_code=201)
async def admin_create_certification(
    data: schemas.CertificationCreate,
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
    if await crud.get_product(database, data.product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    try:
        return await crud.create_certification(database, data)
    except IntegrityError as exc:
        await database.rollback()
        raise HTTPException(status_code=409, detail="Certificate number already exists.") from exc


@router.get("/admin/reports", response_model=list[schemas.ReportResponse])
async def admin_reports(_: models.User = Depends(auth.get_admin_user), database: AsyncSession = Depends(get_database)):
    return await crud.list_reports(database)


@router.patch("/admin/reports/{report_id}", response_model=schemas.ReportResponse)
async def admin_update_report(
    report_id: uuid.UUID,
    data: schemas.ReportUpdate,
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
    report = await database.get(models.Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    return await crud.update_report(database, report, data.status)
