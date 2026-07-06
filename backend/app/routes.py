from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, crud, models, schemas, services
from app.database import get_database


router = APIRouter()


@router.post("/auth/register", response_model=schemas.AuthResponse, status_code=201)
async def register(data: schemas.UserCreate, database: AsyncSession = Depends(get_database)):
    if await crud.get_user_by_email(database, data.email):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = await crud.create_user(database, data, auth.hash_password(data.password))
    return schemas.AuthResponse(access_token=auth.create_access_token(user), user=user)


@router.post("/auth/login", response_model=schemas.AuthResponse)
async def login(data: schemas.UserLogin, database: AsyncSession = Depends(get_database)):
    user = await crud.get_user_by_email(database, data.email)
    if user is None or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return schemas.AuthResponse(access_token=auth.create_access_token(user), user=user)


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


@router.get("/products/search", response_model=list[schemas.ProductSummary])
async def products_search(
    q: str = Query(default="", max_length=120),
    database: AsyncSession = Depends(get_database),
):
    return await crud.search_products(database, q)


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
    return await crud.update_product(database, product, data)


@router.get("/ingredients", response_model=list[schemas.IngredientResponse])
async def ingredients(
    q: str = Query(default="", max_length=120),
    database: AsyncSession = Depends(get_database),
):
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
async def history(
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
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
async def favorites(
    user: models.User = Depends(auth.get_current_user),
    database: AsyncSession = Depends(get_database),
):
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
    user: models.User | None = Depends(auth.get_optional_user),
    database: AsyncSession = Depends(get_database),
):
    return await crud.create_report(database, user.id if user else None, data)


@router.get("/admin/dashboard", response_model=schemas.AdminDashboard)
async def admin_dashboard(
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
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
async def admin_certifications(
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
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
async def admin_reports(
    _: models.User = Depends(auth.get_admin_user),
    database: AsyncSession = Depends(get_database),
):
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
