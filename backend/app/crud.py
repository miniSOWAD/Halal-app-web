from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas


async def get_user_by_email(database: AsyncSession, email: str) -> models.User | None:
    result = await database.execute(select(models.User).where(func.lower(models.User.email) == email.lower()))
    return result.scalar_one_or_none()


async def get_user(database: AsyncSession, user_id: uuid.UUID) -> models.User | None:
    return await database.get(models.User, user_id)


async def create_user(database: AsyncSession, data: schemas.UserCreate, password_hash: str) -> models.User:
    user = models.User(
        name=data.name.strip(),
        email=data.email.lower(),
        password_hash=password_hash,
        country=data.country.upper() if data.country else None,
    )
    database.add(user)
    await database.commit()
    await database.refresh(user)
    return user


async def update_user(database: AsyncSession, user: models.User, data: schemas.UserUpdate) -> models.User:
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "country" and value:
            value = value.upper()
        setattr(user, key, value)
    await database.commit()
    await database.refresh(user)
    return user


async def get_product(database: AsyncSession, product_id: uuid.UUID) -> models.Product | None:
    statement = (
        select(models.Product)
        .options(selectinload(models.Product.certifications))
        .where(models.Product.id == product_id)
    )
    result = await database.execute(statement)
    return result.scalar_one_or_none()


async def get_product_by_barcode(database: AsyncSession, barcode: str) -> models.Product | None:
    statement = (
        select(models.Product)
        .options(selectinload(models.Product.certifications))
        .where(models.Product.barcode == barcode)
    )
    result = await database.execute(statement)
    return result.scalar_one_or_none()


async def search_products(database: AsyncSession, query: str, limit: int = 30) -> Sequence[models.Product]:
    cleaned = query.strip()
    statement = select(models.Product).order_by(models.Product.name).limit(limit)
    if cleaned:
        pattern = f"%{cleaned}%"
        statement = statement.where(
            or_(
                models.Product.name.ilike(pattern),
                models.Product.brand.ilike(pattern),
                models.Product.category.ilike(pattern),
                models.Product.barcode == cleaned,
                models.Product.ingredient_text.ilike(pattern),
            )
        )
    result = await database.execute(statement)
    return result.scalars().unique().all()


async def create_product(database: AsyncSession, data: schemas.ProductCreate) -> models.Product:
    product = models.Product(**data.model_dump())
    database.add(product)
    await database.commit()
    await database.refresh(product)
    return product


async def update_product(
    database: AsyncSession, product: models.Product, data: schemas.ProductUpdate
) -> models.Product:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    await database.commit()
    return await get_product(database, product.id)  # type: ignore[return-value]


async def list_ingredients(database: AsyncSession, query: str = "", limit: int = 100) -> Sequence[models.Ingredient]:
    statement = select(models.Ingredient).order_by(models.Ingredient.name).limit(limit)
    if query.strip():
        pattern = f"%{query.strip()}%"
        statement = statement.where(
            or_(models.Ingredient.name.ilike(pattern), models.Ingredient.e_number.ilike(pattern))
        )
    result = await database.execute(statement)
    return result.scalars().all()


async def all_ingredients(database: AsyncSession) -> Sequence[models.Ingredient]:
    result = await database.execute(select(models.Ingredient))
    return result.scalars().all()


async def active_halal_rules(database: AsyncSession) -> Sequence[models.HalalRule]:
    result = await database.execute(
        select(models.HalalRule)
        .where(models.HalalRule.active.is_(True))
        .order_by(models.HalalRule.priority.desc())
    )
    return result.scalars().all()


async def active_health_rules(database: AsyncSession) -> Sequence[models.HealthRule]:
    result = await database.execute(select(models.HealthRule).where(models.HealthRule.active.is_(True)))
    return result.scalars().all()


async def create_ingredient(database: AsyncSession, data: schemas.IngredientCreate) -> models.Ingredient:
    ingredient = models.Ingredient(**data.model_dump())
    database.add(ingredient)
    await database.commit()
    await database.refresh(ingredient)
    return ingredient


async def update_ingredient(
    database: AsyncSession, ingredient: models.Ingredient, data: schemas.IngredientUpdate
) -> models.Ingredient:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ingredient, key, value)
    await database.commit()
    await database.refresh(ingredient)
    return ingredient


async def get_ingredient(database: AsyncSession, ingredient_id: uuid.UUID) -> models.Ingredient | None:
    return await database.get(models.Ingredient, ingredient_id)


async def list_certifications(database: AsyncSession, limit: int = 100) -> Sequence[models.Certification]:
    result = await database.execute(
        select(models.Certification).order_by(models.Certification.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


async def find_certificate_by_number(database: AsyncSession, number: str) -> models.Certification | None:
    result = await database.execute(
        select(models.Certification)
        .options(selectinload(models.Certification.product))
        .where(func.lower(models.Certification.certificate_number) == number.lower())
    )
    return result.scalar_one_or_none()


async def create_certification(
    database: AsyncSession, data: schemas.CertificationCreate
) -> models.Certification:
    certification = models.Certification(**data.model_dump())
    database.add(certification)
    await database.commit()
    await database.refresh(certification)
    return certification


async def save_scan(
    database: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    product_id: uuid.UUID | None,
    input_type: str,
    input_value: str | None,
    extracted_text: str | None,
    result: dict,
) -> models.Scan:
    scan = models.Scan(
        user_id=user_id,
        product_id=product_id,
        input_type=input_type,
        input_value=input_value,
        extracted_text=extracted_text,
        halal_status=result["halal"]["status"],
        halal_confidence=result["halal"]["confidence"],
        health_status=result["health"]["status"],
        health_score=result["health"]["score"],
        result_json=result,
    )
    database.add(scan)
    await database.commit()
    await database.refresh(scan)
    return scan


async def get_scan(database: AsyncSession, scan_id: uuid.UUID) -> models.Scan | None:
    statement = select(models.Scan).options(selectinload(models.Scan.product)).where(models.Scan.id == scan_id)
    result = await database.execute(statement)
    return result.scalar_one_or_none()


async def get_history(database: AsyncSession, user_id: uuid.UUID, limit: int = 100) -> Sequence[models.Scan]:
    statement = (
        select(models.Scan)
        .options(selectinload(models.Scan.product))
        .where(models.Scan.user_id == user_id)
        .order_by(models.Scan.created_at.desc())
        .limit(limit)
    )
    result = await database.execute(statement)
    return result.scalars().all()


async def delete_scan(database: AsyncSession, scan_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    result = await database.execute(
        delete(models.Scan).where(models.Scan.id == scan_id, models.Scan.user_id == user_id)
    )
    await database.commit()
    return bool(result.rowcount)


async def get_favorites(database: AsyncSession, user_id: uuid.UUID) -> Sequence[models.Favorite]:
    statement = (
        select(models.Favorite)
        .options(selectinload(models.Favorite.product))
        .where(models.Favorite.user_id == user_id)
        .order_by(models.Favorite.created_at.desc())
    )
    result = await database.execute(statement)
    return result.scalars().all()


async def add_favorite(database: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID) -> models.Favorite:
    existing = await database.execute(
        select(models.Favorite).where(
            models.Favorite.user_id == user_id,
            models.Favorite.product_id == product_id,
        )
    )
    favorite = existing.scalar_one_or_none()
    if favorite:
        return favorite
    favorite = models.Favorite(user_id=user_id, product_id=product_id)
    database.add(favorite)
    await database.commit()
    await database.refresh(favorite)
    return favorite


async def remove_favorite(database: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
    result = await database.execute(
        delete(models.Favorite).where(
            models.Favorite.user_id == user_id,
            models.Favorite.product_id == product_id,
        )
    )
    await database.commit()
    return bool(result.rowcount)


async def create_report(
    database: AsyncSession, user_id: uuid.UUID | None, data: schemas.ReportCreate
) -> models.Report:
    report = models.Report(user_id=user_id, **data.model_dump())
    database.add(report)
    await database.commit()
    await database.refresh(report)
    return report


async def list_reports(database: AsyncSession, limit: int = 200) -> Sequence[models.Report]:
    result = await database.execute(select(models.Report).order_by(models.Report.created_at.desc()).limit(limit))
    return result.scalars().all()


async def update_report(database: AsyncSession, report: models.Report, status: str) -> models.Report:
    report.status = status
    await database.commit()
    await database.refresh(report)
    return report


async def get_better_alternatives(
    database: AsyncSession,
    *,
    product: models.Product | None,
    health_score: int,
    limit: int = 3,
) -> Sequence[models.Product]:
    statement = (
        select(models.Product)
        .where(
            models.Product.health_score > health_score,
            models.Product.halal_status.in_(["CERTIFIED_HALAL", "NO_PROHIBITED_INGREDIENT_FOUND"]),
        )
        .order_by(models.Product.health_score.desc())
        .limit(limit)
    )
    if product and product.category:
        statement = statement.where(models.Product.category == product.category)
    if product:
        statement = statement.where(models.Product.id != product.id)
    result = await database.execute(statement)
    return result.scalars().all()


async def dashboard_counts(database: AsyncSession) -> dict[str, int]:
    async def count(model, *criteria) -> int:
        statement = select(func.count()).select_from(model)
        if criteria:
            statement = statement.where(*criteria)
        result = await database.execute(statement)
        return int(result.scalar_one())

    return {
        "users": await count(models.User),
        "products": await count(models.Product),
        "ingredients": await count(models.Ingredient),
        "scans": await count(models.Scan),
        "open_reports": await count(models.Report, models.Report.status != "RESOLVED"),
    }
