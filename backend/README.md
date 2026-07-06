# HalalFit FastAPI backend

## Setup

1. Copy `.env.example` to `.env`.
2. Paste the pooled and direct connection URLs from your Neon dashboard.
3. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

4. Run migrations and seed data:

```bash
alembic upgrade head
python scripts/seed_database.py
```

5. Start the API:

```bash
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

The Docker image includes Tesseract OCR. When running without Docker, install Tesseract on the host system before using image scans.
