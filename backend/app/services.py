from __future__ import annotations

import io
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
import pytesseract
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError
from sqlalchemy.ext.asyncio import AsyncSession

from app import analysis, crud, models, schemas
from app.config import settings


async def fetch_open_food_facts(barcode: str) -> dict[str, Any] | None:
    fields = ",".join(
        [
            "code",
            "product_name",
            "brands",
            "categories",
            "countries_tags",
            "image_front_url",
            "ingredients_text",
            "nutriments",
        ]
    )
    url = f"{settings.open_food_facts_url.rstrip('/')}/api/v2/product/{barcode}.json"
    headers = {"User-Agent": settings.open_food_facts_user_agent}
    try:
        async with httpx.AsyncClient(timeout=12, headers=headers, follow_redirects=True) as client:
            response = await client.get(url, params={"fields": fields})
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    if payload.get("status") != 1 or not payload.get("product"):
        return None
    return payload["product"]


def map_open_food_facts(product: dict[str, Any], barcode: str) -> schemas.ProductCreate:
    nutriments = product.get("nutriments") or {}
    nutrition = {
        "energy_kcal_100g": nutriments.get("energy-kcal_100g"),
        "sugars_100g": nutriments.get("sugars_100g"),
        "saturated_fat_100g": nutriments.get("saturated-fat_100g"),
        "trans_fat_100g": nutriments.get("trans-fat_100g"),
        "sodium_100g": nutriments.get("sodium_100g"),
        "salt_100g": nutriments.get("salt_100g"),
        "fiber_100g": nutriments.get("fiber_100g"),
        "proteins_100g": nutriments.get("proteins_100g"),
    }
    nutrition = {key: value for key, value in nutrition.items() if value is not None}
    name = product.get("product_name") or f"Product {barcode}"
    brand = product.get("brands")
    categories = product.get("categories")
    return schemas.ProductCreate(
        name=name.strip(),
        brand=brand.split(",")[0].strip() if brand else None,
        category=categories.split(",")[0].strip() if categories else None,
        barcode=barcode,
        image_url=product.get("image_front_url"),
        ingredient_text=product.get("ingredients_text"),
        nutrition_data=nutrition,
        data_source="OPEN_FOOD_FACTS",
    )


def extract_text_from_image(content: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(content))
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a readable image.") from exc

    image = ImageOps.exif_transpose(image).convert("L")
    image.thumbnail((2400, 2400))
    image = ImageEnhance.Contrast(image).enhance(1.8)
    try:
        text = pytesseract.image_to_string(image, config="--psm 6")
    except pytesseract.TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="OCR is not installed on the backend server. Install Tesseract or use the provided Dockerfile.",
        ) from exc
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 3:
        raise HTTPException(status_code=422, detail="No readable text was found. Take a clearer label photo.")
    return text


def find_ingredient_text(ocr_text: str) -> str:
    compact = re.sub(r"\r", "", ocr_text)
    match = re.search(
        r"(?is)ingredients?\s*[:\-]\s*(.+?)(?:\n\s*(?:nutrition|allergen|contains|storage|best before|manufactured|distributed)\b|$)",
        compact,
    )
    if match:
        return match.group(1).strip()
    lines = [line.strip() for line in compact.splitlines() if line.strip()]
    likely = [line for line in lines if "," in line or ";" in line]
    return max(likely, key=len) if likely else compact


def parse_nutrition_from_text(text: str) -> dict[str, float]:
    patterns = {
        "sugars_100g": r"(?:total\s+)?sugars?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g",
        "saturated_fat_100g": r"saturat(?:ed|es)\s*(?:fat)?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g",
        "trans_fat_100g": r"trans\s*fat\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g",
        "sodium_100g": r"sodium\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(mg|g)",
        "salt_100g": r"salt\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g",
        "fiber_100g": r"(?:dietary\s+)?fib(?:er|re)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g",
        "proteins_100g": r"protein\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g",
        "energy_kcal_100g": r"(?:energy|calories?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*k?cal",
    }
    values: dict[str, float] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        value = float(match.group(1))
        if key == "sodium_100g" and len(match.groups()) > 1 and match.group(2).lower() == "g":
            value *= 1000
        values[key] = value
    return values


async def build_analysis(
    database: AsyncSession,
    *,
    ingredient_text: str,
    nutrition_data: dict[str, Any] | None,
    input_type: str,
    input_value: str | None,
    user: models.User | None,
    product: models.Product | None = None,
    extracted_text: str | None = None,
) -> schemas.AnalysisResponse:
    ingredient_records = await crud.all_ingredients(database)
    halal_rules = await crud.active_halal_rules(database)
    health_rules = await crud.active_health_rules(database)

    ingredient_names = analysis.split_ingredients(ingredient_text)
    matches = [
        analysis.match_ingredient(name, ingredient_records, halal_rules)
        for name in ingredient_names
    ]
    certificate = analysis.active_certificate(product.certifications if product else [])
    halal = analysis.calculate_halal(matches, certificate)
    health = analysis.calculate_health(matches, nutrition_data, health_rules)
    recommendation = analysis.recommendation(halal, health)

    if product:
        product.ingredient_text = ingredient_text or product.ingredient_text
        if nutrition_data:
            product.nutrition_data = nutrition_data
        product.halal_status = halal["status"]
        product.halal_confidence = halal["confidence"]
        product.health_status = health["status"]
        product.health_score = health["score"]
        product.explanation = recommendation
        await database.flush()

    alternatives = await crud.get_better_alternatives(
        database,
        product=product,
        health_score=health["score"],
    )

    product_payload = None
    if product:
        product_payload = {
            "id": str(product.id),
            "name": product.name,
            "brand": product.brand,
            "barcode": product.barcode,
            "image_url": product.image_url,
        }
    elif input_type == "INGREDIENT_TEXT":
        product_payload = {
            "id": None,
            "name": "Custom ingredient check",
            "brand": None,
            "barcode": None,
            "image_url": None,
        }
    elif input_type == "LABEL_IMAGE":
        product_payload = {
            "id": None,
            "name": "Scanned food label",
            "brand": None,
            "barcode": None,
            "image_url": None,
        }

    result_without_scan = {
        "input_type": input_type,
        "product": product_payload,
        "extracted_text": extracted_text,
        "ingredients": [
            {
                "name": match.original,
                "status": match.status,
                "health_status": match.health_status,
                "reason": match.reason,
                "matched": match.matched,
            }
            for match in matches
        ],
        "halal": halal,
        "health": health,
        "recommendation": recommendation,
        "alternatives": [
            {
                "id": str(item.id),
                "name": item.name,
                "brand": item.brand,
                "image_url": item.image_url,
                "health_score": item.health_score,
                "halal_status": item.halal_status,
            }
            for item in alternatives
        ],
    }

    scan = await crud.save_scan(
        database,
        user_id=user.id if user else None,
        product_id=product.id if product else None,
        input_type=input_type,
        input_value=input_value,
        extracted_text=extracted_text,
        result=result_without_scan,
    )
    result = {
        "scan_id": str(scan.id),
        **result_without_scan,
        "created_at": scan.created_at.isoformat(),
    }
    scan.result_json = result
    await database.commit()
    return schemas.AnalysisResponse.model_validate(result)


async def analyze_product(
    database: AsyncSession,
    product: models.Product,
    *,
    user: models.User | None,
    input_type: str,
    input_value: str | None,
) -> schemas.AnalysisResponse:
    return await build_analysis(
        database,
        ingredient_text=product.ingredient_text or "",
        nutrition_data=product.nutrition_data,
        input_type=input_type,
        input_value=input_value,
        user=user,
        product=product,
    )


def code_candidate(value: str) -> str | None:
    stripped = value.strip()
    if re.fullmatch(r"\d{8,14}", stripped):
        return stripped
    if not stripped.lower().startswith(("http://", "https://")):
        return None
    parsed = urlparse(stripped)
    query = parse_qs(parsed.query)
    for key in ("barcode", "gtin", "code"):
        candidate = query.get(key, [None])[0]
        if candidate and re.fullmatch(r"\d{8,14}", candidate):
            return candidate
    for segment in reversed([part for part in parsed.path.split("/") if part]):
        if re.fullmatch(r"\d{8,14}", segment):
            return segment
    return None


async def analyze_code(
    database: AsyncSession,
    data: schemas.CodeScanRequest,
    user: models.User | None,
) -> schemas.AnalysisResponse:
    raw_code = data.code.strip()
    barcode = code_candidate(raw_code)

    if not barcode:
        certificate = await crud.find_certificate_by_number(database, raw_code)
        if certificate:
            return await analyze_product(
                database,
                certificate.product,
                user=user,
                input_type="QR_CODE",
                input_value=raw_code,
            )
        return await build_analysis(
            database,
            ingredient_text="",
            nutrition_data=None,
            input_type="QR_CODE",
            input_value=raw_code,
            user=user,
            extracted_text="The QR code did not contain a supported product barcode or certificate number.",
        )

    product = await crud.get_product_by_barcode(database, barcode)
    if product is None:
        external = await fetch_open_food_facts(barcode)
        if external:
            product = await crud.create_product(database, map_open_food_facts(external, barcode))
            product = await crud.get_product(database, product.id)

    if product is None:
        return await build_analysis(
            database,
            ingredient_text="",
            nutrition_data=None,
            input_type="BARCODE" if data.format != "QR_CODE" else "QR_CODE",
            input_value=raw_code,
            user=user,
            extracted_text=f"No product data was found for barcode {barcode}.",
        )

    return await analyze_product(
        database,
        product,
        user=user,
        input_type="QR_CODE" if data.format == "QR_CODE" else "BARCODE",
        input_value=raw_code,
    )


async def analyze_image(
    database: AsyncSession,
    file: UploadFile,
    user: models.User | None,
) -> schemas.AnalysisResponse:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG or WebP image.")
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Image must be smaller than {settings.max_upload_mb} MB.")
    text = extract_text_from_image(content)
    ingredients = find_ingredient_text(text)
    nutrition = parse_nutrition_from_text(text)
    return await build_analysis(
        database,
        ingredient_text=ingredients,
        nutrition_data=nutrition,
        input_type="LABEL_IMAGE",
        input_value=file.filename,
        user=user,
        extracted_text=text,
    )


def scan_from_model(scan: models.Scan) -> schemas.AnalysisResponse:
    payload = dict(scan.result_json)
    payload.setdefault("scan_id", str(scan.id))
    payload.setdefault("created_at", scan.created_at.isoformat())
    return schemas.AnalysisResponse.model_validate(payload)
