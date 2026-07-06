# HalalFit Backend — FastAPI Cloud + Neon

This folder is prepared for:

- FastAPI Cloud for the API
- Neon PostgreSQL for persistent cloud data
- SQLAlchemy async sessions through asyncpg
- Automatic first-run table creation and safe starter-data seeding

The backend never needs to connect to a PostgreSQL server running on your computer.

## Important architecture

```text
Next.js / Android app
        ↓ HTTPS
FastAPI Cloud
        ↓ DATABASE_URL
Neon PostgreSQL
```

FastAPI Cloud runs the API. Neon runs the PostgreSQL database.

## Files cleaned from the uploaded project

The deployment package intentionally excludes:

- `.env`
- `.venv/`
- `__pycache__/`
- `.ruff_cache/`
- generated `*.egg-info/`

Never upload the real `.env` file. Add secrets in FastAPI Cloud instead.

## 1. Install once on Windows

The project uses Python 3.13.

```powershell
cd "D:\Android dev\Halal-app-web\backend"

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Verify the entrypoint:

```powershell
fastapi dev
```

It should start without requiring `app/main.py` because `pyproject.toml` contains:

```toml
[tool.fastapi]
entrypoint = "app.main:app"
```

## 2. Create the FastAPI Cloud app

```powershell
fastapi login
fastapi deploy
```

The first command opens the login page. The deploy command creates or links the cloud app and returns a URL similar to:

```text
https://halalfit-xxxxxxxx.fastapicloud.dev
```

The first deployment may use the local SQLite fallback only to allow the cloud app to be created. Do not use that deployment for real app data. Connect Neon and redeploy next.

## 3. Connect Neon in FastAPI Cloud

In the FastAPI Cloud dashboard:

1. Open team **Integrations**.
2. Connect your Neon account.
3. Open the HalalFit app.
4. Open **Integrations → Neon**.
5. Select the Neon project, branch, and database.
6. Enable redeployment.

FastAPI Cloud creates an encrypted `DATABASE_URL` secret. The code accepts the standard Neon `postgresql://` connection string and converts it to the asyncpg SQLAlchemy format automatically.

You do not need to manually change it to `postgresql+asyncpg://`; the backend normalizes the URL.

## 4. Add cloud environment variables

In the app dashboard, open **Environment Variables** and add:

```env
APP_ENV=production
DEBUG=false
API_PREFIX=/api
JWT_SECRET=GENERATE_A_LONG_RANDOM_SECRET
FRONTEND_URLS=["https://your-frontend-domain.com","capacitor://localhost","https://localhost"]
AUTO_CREATE_TABLES=true
AUTO_SEED_DATA=true
SEED_DEMO_PRODUCTS=false
OPEN_FOOD_FACTS_USER_AGENT=HalalFit/1.0 (your-email@example.com)
```

Mark `JWT_SECRET` as a secret.

### First administrator

For the first deployment only, optionally add these as secrets:

```env
SEED_ADMIN_EMAIL=your-email@example.com
SEED_ADMIN_PASSWORD=YOUR_STRONG_PASSWORD
```

After the administrator is created and login works, remove those two environment variables and redeploy. The user remains in Neon.

### Image OCR

Manual ingredient checking, product search, barcode scanning, and QR-code lookup work without an OCR provider.

For label-image OCR on FastAPI Cloud, configure:

```env
OCR_PROVIDER=ocr_space
OCR_API_KEY=YOUR_OCR_API_KEY
OCR_LANGUAGE=eng
```

Mark `OCR_API_KEY` as a secret. Uploaded label images are sent to the configured OCR provider. Update your privacy policy accordingly.

Without those variables, `/api/scan/image` returns a clear configuration error instead of crashing the API.

## 5. Redeploy

After saving variables and connecting Neon:

```powershell
fastapi deploy
```

Or use **Save and Redeploy** in the dashboard.

On startup, the backend will:

1. Connect to Neon.
2. Create missing tables.
3. Insert the core ingredient and halal-rule data if missing.
4. Create the optional administrator if configured.

The seed process is idempotent and uses a PostgreSQL advisory lock so multiple cloud instances do not seed simultaneously.

## 6. Verify the cloud deployment

Open these URLs using your generated FastAPI Cloud domain:

```text
https://YOUR-APP.fastapicloud.dev/
https://YOUR-APP.fastapicloud.dev/health
https://YOUR-APP.fastapicloud.dev/health/database
https://YOUR-APP.fastapicloud.dev/docs
```

Expected database health response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

## 7. Connect the frontend

In the Next.js frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://YOUR-APP.fastapicloud.dev/api
```

Rebuild the web/Android frontend after changing a `NEXT_PUBLIC_` variable.

Do not put Neon credentials or `JWT_SECRET` in the frontend environment file.

## Database setup behavior

For this MVP, `AUTO_CREATE_TABLES=true` creates missing tables automatically. This is the easiest first deployment.

Alembic remains included for later schema changes. To run migrations manually, set a direct Neon URL locally:

```env
MIGRATION_DATABASE_URL=postgresql://USER:PASSWORD@DIRECT_HOST/neondb?sslmode=require&channel_binding=require
```

Then run:

```powershell
alembic upgrade head
```

For later production schema changes, run migrations carefully before or after deployments depending on whether the change adds or removes fields.

## Useful commands

```powershell
# Local development
fastapi dev

# Tests
pytest

# Lint
ruff check .

# Cloud deployment
fastapi deploy

# Cloud logs
fastapi cloud logs
```

## Deployment lock-file fix

This package intentionally does not include `uv.lock`.

The previous lock file was generated against a private package registry and
contained private registry URLs. FastAPI Cloud followed those URLs during the
build, which caused dependency download timeouts for packages such as
`typing-extensions` and `psycopg-binary`.

FastAPI Cloud can install directly from `pyproject.toml`, so the corrected
package excludes `uv.lock` from deployment. Do not copy the previous lock file
back into this folder.

Deploy with:

```powershell
fastapi deploy
```

If you later want a local lock file, regenerate it on your own computer using a
public package index, and keep it excluded from FastAPI Cloud unless you verify
that it contains only public registry URLs.
