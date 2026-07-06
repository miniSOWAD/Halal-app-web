# HalalFit Global

A minimal full-stack food assistant with separate halal and nutrition results.

## Stack

- Next.js + TypeScript frontend
- Capacitor Android wrapper for Google Play
- FastAPI backend
- SQLAlchemy + Alembic
- Neon PostgreSQL
- Tesseract OCR
- Open Food Facts barcode fallback

## Features

- Product and brand search
- Manual ingredient checker
- Ingredient-label OCR
- Barcode and QR scanning
- Halal / haram / doubtful / unknown verdicts
- Health score and reasons
- Certificate records
- History, favorites and user reports
- Simple admin page

## Start locally

### Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed_database.py
uvicorn app.main:app --reload
```

For Neon, replace both database URLs in `backend/.env` with the pooled and direct URLs from the Neon dashboard.

### Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. FastAPI docs are at `http://localhost:8000/docs`.

The seed script creates a local demo administrator: `admin@halalfit.app` / `ChangeMe123!`. Change it before deployment.

## Color palette

- `#071E22` Dark Jungle Green
- `#1D7874` Myrtle Green
- `#679289` Wintergreen Dream
- `#F4C095` Peach Crayola
- `#EE2E31` Red Pigment

## Accuracy note

The application performs ingredient screening. A result such as “No prohibited ingredient found” is not the same as official halal certification. Unknown and source-dependent ingredients remain unverified.
