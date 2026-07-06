-- HalalFit PostgreSQL schema for Neon
-- Safe to run on a new database. Existing cloud databases are upgraded by app/bootstrap.py.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(120) NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    country VARCHAR(2),
    phone VARCHAR(32),
    email_verified BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS email_otps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) NOT NULL,
    purpose VARCHAR(40) NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    expires_at TIMESTAMPTZ NOT NULL,
    resend_at TIMESTAMPTZ NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    consumed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_email_otps_email ON email_otps (email);
CREATE INDEX IF NOT EXISTS ix_email_otps_purpose ON email_otps (purpose);
CREATE INDEX IF NOT EXISTS ix_email_otps_expires_at ON email_otps (expires_at);
CREATE INDEX IF NOT EXISTS ix_email_otps_consumed ON email_otps (consumed);

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(220) NOT NULL,
    brand VARCHAR(160),
    category VARCHAR(120),
    barcode VARCHAR(32) UNIQUE,
    country VARCHAR(2),
    image_url TEXT,
    ingredient_text TEXT,
    nutrition_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    halal_status VARCHAR(48) NOT NULL DEFAULT 'UNKNOWN',
    halal_confidence INTEGER NOT NULL DEFAULT 0,
    health_status VARCHAR(24) NOT NULL DEFAULT 'UNKNOWN',
    health_score INTEGER NOT NULL DEFAULT 0,
    explanation TEXT,
    data_source VARCHAR(80) NOT NULL DEFAULT 'ADMIN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_products_name ON products (name);
CREATE INDEX IF NOT EXISTS ix_products_brand ON products (brand);
CREATE INDEX IF NOT EXISTS ix_products_category ON products (category);
CREATE INDEX IF NOT EXISTS ix_products_barcode ON products (barcode);

CREATE TABLE IF NOT EXISTS ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
    e_number VARCHAR(20) UNIQUE,
    halal_status VARCHAR(24) NOT NULL DEFAULT 'UNKNOWN',
    health_status VARCHAR(24) NOT NULL DEFAULT 'NEUTRAL',
    source_dependent BOOLEAN NOT NULL DEFAULT FALSE,
    risk_level INTEGER NOT NULL DEFAULT 0 CHECK (risk_level BETWEEN 0 AND 5),
    explanation TEXT NOT NULL DEFAULT 'No explanation available.',
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_ingredients_name ON ingredients (name);
CREATE INDEX IF NOT EXISTS ix_ingredients_e_number ON ingredients (e_number);

CREATE TABLE IF NOT EXISTS product_ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    original_name VARCHAR(240) NOT NULL,
    CONSTRAINT uq_product_ingredient UNIQUE (product_id, ingredient_id)
);
CREATE INDEX IF NOT EXISTS ix_product_ingredients_product_id ON product_ingredients (product_id);
CREATE INDEX IF NOT EXISTS ix_product_ingredients_ingredient_id ON product_ingredients (ingredient_id);

CREATE TABLE IF NOT EXISTS halal_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword VARCHAR(180) NOT NULL UNIQUE,
    status VARCHAR(24) NOT NULL,
    reason TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 10,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS health_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nutrient VARCHAR(80) NOT NULL UNIQUE,
    maximum_value DOUBLE PRECISION,
    minimum_value DOUBLE PRECISION,
    score_change INTEGER NOT NULL,
    message TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    authority_name VARCHAR(180) NOT NULL,
    certificate_number VARCHAR(120) NOT NULL UNIQUE,
    country VARCHAR(2),
    valid_from DATE,
    valid_until DATE,
    verification_url TEXT,
    status VARCHAR(24) NOT NULL DEFAULT 'UNVERIFIED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_certifications_product_id ON certifications (product_id);
CREATE INDEX IF NOT EXISTS ix_certifications_certificate_number ON certifications (certificate_number);

CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    input_type VARCHAR(32) NOT NULL,
    input_value TEXT,
    extracted_text TEXT,
    halal_status VARCHAR(48) NOT NULL DEFAULT 'UNKNOWN',
    halal_confidence INTEGER NOT NULL DEFAULT 0,
    health_status VARCHAR(24) NOT NULL DEFAULT 'UNKNOWN',
    health_score INTEGER NOT NULL DEFAULT 0,
    result_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_scans_user_id ON scans (user_id);
CREATE INDEX IF NOT EXISTS ix_scans_product_id ON scans (product_id);

CREATE TABLE IF NOT EXISTS favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_favorite UNIQUE (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    subject VARCHAR(180) NOT NULL DEFAULT 'User report',
    category VARCHAR(40) NOT NULL DEFAULT 'GENERAL',
    message TEXT NOT NULL,
    status VARCHAR(24) NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_reports_user_id ON reports (user_id);
CREATE INDEX IF NOT EXISTS ix_reports_product_id ON reports (product_id);
