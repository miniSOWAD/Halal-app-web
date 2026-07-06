"""Import product JSON using the same analysis engine as the API.

Usage:
    python scripts/import_products.py data/sample-products.json
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from app import crud, schemas, services
from app.database import SessionFactory


async def import_file(path: Path) -> None:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("The JSON file must contain a list of products.")

    created = 0
    skipped = 0
    async with SessionFactory() as database:
        for raw in rows:
            data = schemas.ProductCreate.model_validate(raw)
            if data.barcode and await crud.get_product_by_barcode(database, data.barcode):
                skipped += 1
                continue
            try:
                product = await crud.create_product(database, data)
                if product.ingredient_text or product.nutrition_data:
                    await services.refresh_product_assessment(database, product)
                created += 1
            except IntegrityError:
                await database.rollback()
                skipped += 1
    print(f"Imported {created} product(s); skipped {skipped} duplicate(s).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/import_products.py <products.json>")
    asyncio.run(import_file(Path(sys.argv[1])))
