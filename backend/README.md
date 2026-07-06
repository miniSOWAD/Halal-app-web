# HalalFit FastAPI backend

FastAPI + SQLAlchemy + Neon PostgreSQL backend for HalalFit.

## FastAPI Cloud environment variables

Set these in **FastAPI Cloud → backend app → Environment Variables**, then redeploy:

```env
APP_NAME=HalalFit Global
APP_ENV=production
DEBUG=false
API_PREFIX=/api
DATABASE_URL=<Neon pooled URL>
JWT_SECRET=<long random secret>
CORS_ALLOW_ALL=true
AUTO_CREATE_TABLES=true
AUTO_SEED_DATA=true
SEED_DEMO_PRODUCTS=true

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=baisakh2015@gmail.com
SMTP_PASSWORD=<Google 16-character App Password>
SMTP_FROM_EMAIL=baisakh2015@gmail.com
SMTP_FROM_NAME=HalalFit
CONTACT_RECEIVER_EMAIL=baisakh2015@gmail.com
OTP_EXPIRE_SECONDS=120
OTP_RESEND_SECONDS=60
OTP_MAX_ATTEMPTS=5
```

`SMTP_PASSWORD` must be a Google App Password, not the normal Gmail password. Enable 2-Step Verification on the Google account first.

Mark `DATABASE_URL`, `JWT_SECRET`, and `SMTP_PASSWORD` as secrets.

## Deployment

```powershell
fastapi deploy
```

After deployment check:

- `/health`
- `/health/database`
- `/health/config` — `email_configured` must be `true`
- `/docs`

The startup process creates missing tables and applies the small profile/OTP schema upgrade to an existing Neon database.

## Authentication flow

- `POST /api/auth/register/send-otp`
- `POST /api/auth/register/verify-otp`
- `POST /api/auth/register/resend-otp`
- `POST /api/auth/login`
- `POST /api/auth/forgot-password/send-otp`
- `POST /api/auth/forgot-password/verify-otp`
- `POST /api/auth/forgot-password/reset`
- `POST /api/auth/email-change/send-otp`
- `POST /api/auth/email-change/verify-otp`
- `POST /api/auth/password/change`

OTPs expire after 2 minutes. Resending is allowed after 1 minute.

## Product data schema

Files under `data/`:

- `product-import.schema.json` — JSON Schema
- `sample-products.json` — valid example
- `products-template.csv` — spreadsheet template

The best way to add a product is through the admin page or `POST /api/products`. This automatically recalculates halal and health results.

For a JSON batch:

```powershell
python scripts/import_products.py data/sample-products.json
```

## Local development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
fastapi dev
```
