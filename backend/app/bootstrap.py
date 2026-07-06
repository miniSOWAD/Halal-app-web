from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select, text

from app.auth import hash_password
from app.config import settings
from app.database import SessionFactory
from app.models import Certification, HalalRule, HealthRule, Ingredient, Product, User

INGREDIENTS = [{'name': 'Pork',
  'aliases': ['pig meat', 'swine'],
  'halal_status': 'HARAM',
  'health_status': 'NEUTRAL',
  'risk_level': 5,
  'explanation': 'Pork is prohibited in Islamic dietary law.'},
 {'name': 'Lard',
  'aliases': ['pork fat'],
  'halal_status': 'HARAM',
  'health_status': 'UNHEALTHY',
  'risk_level': 5,
  'explanation': 'Lard is fat derived from pigs.'},
 {'name': 'Bacon',
  'aliases': [],
  'halal_status': 'HARAM',
  'health_status': 'UNHEALTHY',
  'risk_level': 5,
  'explanation': 'Bacon normally refers to cured pork unless another source is clearly stated.'},
 {'name': 'Ham',
  'aliases': [],
  'halal_status': 'HARAM',
  'health_status': 'UNHEALTHY',
  'risk_level': 5,
  'explanation': 'Ham normally refers to pork unless another source is clearly stated.'},
 {'name': 'Blood',
  'aliases': ['blood plasma'],
  'halal_status': 'HARAM',
  'health_status': 'NEUTRAL',
  'risk_level': 5,
  'explanation': 'Consumed blood and blood-derived food ingredients are prohibited.'},
 {'name': 'Wine',
  'aliases': ['cooking wine'],
  'halal_status': 'HARAM',
  'health_status': 'UNHEALTHY',
  'risk_level': 5,
  'explanation': 'Wine is an intoxicating alcoholic beverage.'},
 {'name': 'Beer',
  'aliases': [],
  'halal_status': 'HARAM',
  'health_status': 'UNHEALTHY',
  'risk_level': 5,
  'explanation': 'Beer is an intoxicating alcoholic beverage.'},
 {'name': 'Rum',
  'aliases': [],
  'halal_status': 'HARAM',
  'health_status': 'UNHEALTHY',
  'risk_level': 5,
  'explanation': 'Rum is an intoxicating alcoholic beverage.'},
 {'name': 'Ethanol',
  'aliases': ['ethyl alcohol', 'alcohol'],
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 4,
  'explanation': 'The source, amount and purpose of alcohol must be verified; do not infer the ruling from '
                 'the word alone.'},
 {'name': 'Gelatin',
  'aliases': ['gelatine'],
  'e_number': 'E441',
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 4,
  'explanation': 'Gelatin may come from pork, non-halal beef, halal-certified beef, fish or other sources.'},
 {'name': 'Mono- and diglycerides',
  'aliases': ['mono and diglycerides', 'mono diglycerides'],
  'e_number': 'E471',
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 3,
  'explanation': 'E471 can be produced from plant or animal fats, so the source should be confirmed.'},
 {'name': 'Fatty acid esters',
  'aliases': ['mono and diglyceride esters'],
  'e_number': 'E472',
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 3,
  'explanation': 'E472 additives may use plant or animal-derived fatty acids.'},
 {'name': 'Rennet',
  'aliases': [],
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 3,
  'explanation': 'Rennet may be microbial, plant-based or animal-derived; animal source and slaughter status '
                 'matter.'},
 {'name': 'Pepsin',
  'aliases': [],
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 4,
  'explanation': 'Pepsin is commonly animal-derived and requires source verification.'},
 {'name': 'Enzymes',
  'aliases': ['enzyme'],
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 3,
  'explanation': 'The source of unspecified enzymes may be microbial, plant or animal.'},
 {'name': 'Natural flavoring',
  'aliases': ['natural flavouring', 'natural flavor', 'natural flavour'],
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 2,
  'explanation': 'The source and carrier of unspecified natural flavouring may need verification.'},
 {'name': 'Carmine',
  'aliases': ['cochineal', 'carminic acid'],
  'e_number': 'E120',
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 2,
  'explanation': 'Carmine is insect-derived and its acceptance differs between halal authorities.'},
 {'name': 'Whey',
  'aliases': ['whey powder'],
  'halal_status': 'DOUBTFUL',
  'health_status': 'NEUTRAL',
  'source_dependent': True,
  'risk_level': 2,
  'explanation': 'Whey can be affected by the enzymes used during cheese production.'},
 {'name': 'Animal shortening',
  'aliases': ['animal fat', 'shortening animal'],
  'halal_status': 'DOUBTFUL',
  'health_status': 'UNHEALTHY',
  'source_dependent': True,
  'risk_level': 4,
  'explanation': 'The animal species and halal status of the source must be verified.'},
 {'name': 'Sugar',
  'aliases': ['sucrose', 'cane sugar'],
  'halal_status': 'HALAL',
  'health_status': 'UNHEALTHY',
  'risk_level': 2,
  'explanation': 'Sugar is generally permissible, but high intake should be limited.'},
 {'name': 'Glucose syrup',
  'aliases': ['corn syrup', 'glucose-fructose syrup'],
  'halal_status': 'HALAL',
  'health_status': 'UNHEALTHY',
  'risk_level': 3,
  'explanation': 'Usually plant-derived and permissible; frequent high intake contributes to high sugar '
                 'consumption.'},
 {'name': 'Wheat flour',
  'aliases': ['flour', 'whole wheat flour'],
  'halal_status': 'HALAL',
  'health_status': 'NEUTRAL',
  'risk_level': 0,
  'explanation': 'Wheat flour is plant-derived and generally permissible.'},
 {'name': 'Vegetable oil',
  'aliases': ['canola oil', 'sunflower oil', 'palm oil', 'soybean oil'],
  'halal_status': 'HALAL',
  'health_status': 'NEUTRAL',
  'risk_level': 1,
  'explanation': 'Vegetable oils are plant-derived and generally permissible.'},
 {'name': 'Milk powder',
  'aliases': ['skim milk powder', 'whole milk powder'],
  'halal_status': 'HALAL',
  'health_status': 'NEUTRAL',
  'risk_level': 0,
  'explanation': 'Plain milk powder is generally permissible.'},
 {'name': 'Cocoa powder',
  'aliases': ['cocoa mass', 'cocoa solids'],
  'halal_status': 'HALAL',
  'health_status': 'NEUTRAL',
  'risk_level': 0,
  'explanation': 'Plain cocoa ingredients are plant-derived and generally permissible.'},
 {'name': 'Soy lecithin',
  'aliases': ['lecithin', 'sunflower lecithin'],
  'e_number': 'E322',
  'halal_status': 'HALAL',
  'health_status': 'NEUTRAL',
  'risk_level': 0,
  'explanation': 'Plant-derived lecithin is generally permissible.'},
 {'name': 'Salt',
  'aliases': ['sodium chloride'],
  'halal_status': 'HALAL',
  'health_status': 'NEUTRAL',
  'risk_level': 1,
  'explanation': 'Salt is permissible, but high sodium intake should be limited.'},
 {'name': 'Water',
  'aliases': [],
  'halal_status': 'HALAL',
  'health_status': 'HEALTHY',
  'risk_level': 0,
  'explanation': 'Water is permissible.'},
 {'name': 'Oats',
  'aliases': ['rolled oats', 'oat flour'],
  'halal_status': 'HALAL',
  'health_status': 'HEALTHY',
  'risk_level': 0,
  'explanation': 'Plain oats are plant-derived and generally permissible.'},
 {'name': 'Dates',
  'aliases': ['date paste'],
  'halal_status': 'HALAL',
  'health_status': 'HEALTHY',
  'risk_level': 0,
  'explanation': 'Dates are plant-derived and generally permissible.'}]

HALAL_RULES = [('pork', 'HARAM', 'Pork is prohibited.', 100),
 ('lard', 'HARAM', 'Lard is pork-derived fat.', 100),
 ('bacon', 'HARAM', 'Bacon normally indicates pork unless another source is specified.', 90),
 ('gelatin', 'DOUBTFUL', 'The source of gelatin must be verified.', 70),
 ('e471', 'DOUBTFUL', 'E471 may use plant or animal fats.', 70),
 ('e472', 'DOUBTFUL', 'E472 may use plant or animal fatty acids.', 70)]

HEALTH_RULES = []


async def seed_database() -> dict[str, int]:
    """Insert the core rules safely. The function can run more than once."""
    created = {"ingredients": 0, "halal_rules": 0, "health_rules": 0, "products": 0, "admins": 0}

    async with SessionFactory() as database:
        async with database.begin():
            if database.get_bind().dialect.name == "postgresql":
                # Prevent two FastAPI Cloud instances from seeding the same database at once.
                await database.execute(
                    text("SELECT pg_advisory_xact_lock(:lock_key)"),
                    {"lock_key": 485019771},
                )

            for item in INGREDIENTS:
                existing = await database.execute(
                    select(Ingredient.id).where(Ingredient.name == item["name"])
                )
                if existing.scalar_one_or_none() is None:
                    database.add(Ingredient(**item))
                    created["ingredients"] += 1

            for keyword, status, reason, priority in HALAL_RULES:
                existing = await database.execute(
                    select(HalalRule.id).where(HalalRule.keyword == keyword)
                )
                if existing.scalar_one_or_none() is None:
                    database.add(
                        HalalRule(
                            keyword=keyword,
                            status=status,
                            reason=reason,
                            priority=priority,
                        )
                    )
                    created["halal_rules"] += 1

            for nutrient, maximum, minimum, score, message in HEALTH_RULES:
                existing = await database.execute(
                    select(HealthRule.id).where(HealthRule.nutrient == nutrient)
                )
                if existing.scalar_one_or_none() is None:
                    database.add(
                        HealthRule(
                            nutrient=nutrient,
                            maximum_value=maximum,
                            minimum_value=minimum,
                            score_change=score,
                            message=message,
                        )
                    )
                    created["health_rules"] += 1

            if settings.seed_admin_email and settings.seed_admin_password:
                admin_email = settings.seed_admin_email.strip().lower()
                existing = await database.execute(select(User.id).where(User.email == admin_email))
                if existing.scalar_one_or_none() is None:
                    database.add(
                        User(
                            name="HalalFit Admin",
                            email=admin_email,
                            password_hash=hash_password(settings.seed_admin_password),
                            is_admin=True,
                        )
                    )
                    created["admins"] += 1

            if settings.seed_demo_products:
                sample_rows = [
                    {
                        "name": "Whole Grain Date Bar",
                        "brand": "HalalFit Demo",
                        "category": "Snack bars",
                        "barcode": "9501234567001",
                        "ingredient_text": "Oats, dates, cocoa powder, sunflower oil",
                        "nutrition_data": {
                            "sugars_100g": 16,
                            "saturated_fat_100g": 1.5,
                            "fiber_100g": 7,
                            "proteins_100g": 8,
                            "sodium_100g": 80,
                        },
                        "halal_status": "CERTIFIED_HALAL",
                        "halal_confidence": 95,
                        "health_status": "HEALTHY",
                        "health_score": 88,
                        "data_source": "DEMO",
                    },
                    {
                        "name": "Chocolate Wafer",
                        "brand": "HalalFit Demo",
                        "category": "Biscuits",
                        "barcode": "9501234567002",
                        "ingredient_text": "Sugar, wheat flour, vegetable oil, cocoa powder, E471, milk powder",
                        "nutrition_data": {
                            "sugars_100g": 31,
                            "saturated_fat_100g": 8,
                            "fiber_100g": 2,
                            "proteins_100g": 5,
                            "sodium_100g": 310,
                        },
                        "halal_status": "DOUBTFUL",
                        "halal_confidence": 82,
                        "health_status": "UNHEALTHY",
                        "health_score": 34,
                        "data_source": "DEMO",
                    },
                ]
                for row in sample_rows:
                    existing = await database.execute(
                        select(Product.id).where(Product.barcode == row["barcode"])
                    )
                    if existing.scalar_one_or_none() is None:
                        database.add(Product(**row))
                        created["products"] += 1

                await database.flush()
                demo_product = (
                    await database.execute(
                        select(Product).where(Product.barcode == "9501234567001")
                    )
                ).scalar_one_or_none()
                if demo_product:
                    existing = await database.execute(
                        select(Certification.id).where(
                            Certification.certificate_number == "DEMO-HALAL-001"
                        )
                    )
                    if existing.scalar_one_or_none() is None:
                        database.add(
                            Certification(
                                product_id=demo_product.id,
                                authority_name="Demo Certification Authority",
                                certificate_number="DEMO-HALAL-001",
                                country="MY",
                                valid_from=date.today() - timedelta(days=30),
                                valid_until=date.today() + timedelta(days=335),
                                status="ACTIVE",
                            )
                        )

    return created


async def upgrade_existing_schema(connection) -> None:
    """Apply small idempotent PostgreSQL upgrades for existing Neon databases.

    create_all creates new tables but does not add columns to tables that already
    exist. These statements keep cloud redeployment simple for the MVP.
    """
    if connection.dialect.name != "postgresql":
        return
    statements = [
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS phone VARCHAR(32)",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT TRUE",
        "ALTER TABLE IF EXISTS reports ADD COLUMN IF NOT EXISTS subject VARCHAR(180) NOT NULL DEFAULT 'User report'",
        "ALTER TABLE IF EXISTS reports ADD COLUMN IF NOT EXISTS category VARCHAR(40) NOT NULL DEFAULT 'GENERAL'",
    ]
    for statement in statements:
        await connection.execute(text(statement))
