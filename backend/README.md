# HalalFit FastAPI backend

The backend uses FastAPI, SQLAlchemy, Alembic, and Neon PostgreSQL.

## 1. Configure the environment

Copy `.env.example` to `.env` and add the two URLs from Neon:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@POOLER_HOST/neondb?ssl=require
MIGRATION_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@DIRECT_HOST/neondb?sslmode=require
JWT_SECRET=replace-with-a-long-random-secret
```

- `DATABASE_URL` is the pooled URL used by FastAPI.
- `MIGRATION_DATABASE_URL` is the direct URL used by Alembic.

## 2. Install dependencies

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then install:

```bash
pip install -e ".[dev]"
```

## 3. Create the database tables

Use **one** of these methods on a new Neon database.

### Recommended: Alembic

```bash
alembic upgrade head
```

### Alternative: Neon SQL Editor

Open `database.sql`, copy its contents, and run it in the Neon SQL Editor.
The SQL file also records the included Alembic revision, so later migrations can continue normally.

Do not run both methods on the same fresh database.

## 4. Add starter data

```bash
python scripts/seed_database.py
```

This adds starter ingredients, halal rules, health rules, demo products, and the demo administrator.

## 5. Run FastAPI

```bash
uvicorn app.main:app --reload
```

Useful URLs:

- API documentation: `http://localhost:8000/docs`
- Liveness: `http://localhost:8000/health`
- Neon connection check: `http://localhost:8000/health/database`

## Notes based on the previous backend

The useful patterns retained are centralized settings, async SQLAlchemy sessions, FastAPI dependency injection, JWT helpers, and a real database health check. The HalalFit backend keeps those patterns in fewer files because this project is intended to remain easy to maintain.

Never include `.env` or `.venv` in a project archive or Git repository.
