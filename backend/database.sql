-- HalalFit Global PostgreSQL schema
-- Compatible with Neon PostgreSQL and Alembic revision 5aa2495de664.
-- You may run this file once in the Neon SQL Editor instead of running
-- `alembic upgrade head` on a fresh database.

BEGIN;

CREATE TABLE IF NOT EXISTS halal_rules (
    id UUID PRIMARY KEY,
    keyword VARCHAR(180) NOT NULL,
    status VARCHAR(24) NOT NULL,
    reason TEXT NOT NULL,
    priority INTEGER NOT NULL,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_halal_rules_keyword ON halal_rules (keyword);

CREATE TABLE IF NOT EXISTS health_rules (
    id UUID PRIMARY KEY,
    nutrient VARCHAR(80) NOT NULL,
    maximum_value DOUBLE PRECISION,
    minimum_value DOUBLE PRECISION,
    score_change INTEGER NOT NULL,
    message TEXT NOT NULL,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_health_rules_nutrient ON health_rules (nutrient);

CREATE TABLE IF NOT EXISTS ingredients (
    id UUID PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    aliases JSON NOT NULL,
    e_number VARCHAR(20),
    halal_status VARCHAR(24) NOT NULL,
    health_status VARCHAR(24) NOT NULL,
    source_dependent BOOLEAN NOT NULL,
    risk_level INTEGER NOT NULL,
    explanation TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_ingredients_name ON ingredients (name);
CREATE UNIQUE INDEX IF NOT EXISTS ix_ingredients_e_number ON ingredients (e_number);

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY,
    name VARCHAR(220) NOT NULL,
    brand VARCHAR(160),
    category VARCHAR(120),
    barcode VARCHAR(32),
    country VARCHAR(2),
    image_url TEXT,
    ingredient_text TEXT,
    nutrition_data JSON NOT NULL,
    halal_status VARCHAR(48) NOT NULL,
    halal_confidence INTEGER NOT NULL,
    health_status VARCHAR(24) NOT NULL,
    health_score INTEGER NOT NULL,
    explanation TEXT,
    data_source VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_products_name ON products (name);
CREATE INDEX IF NOT EXISTS ix_products_brand ON products (brand);
CREATE INDEX IF NOT EXISTS ix_products_category ON products (category);
CREATE UNIQUE INDEX IF NOT EXISTS ix_products_barcode ON products (barcode);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(320) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    country VARCHAR(2),
    is_admin BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS certifications (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    authority_name VARCHAR(180) NOT NULL,
    certificate_number VARCHAR(120) NOT NULL,
    country VARCHAR(2),
    valid_from DATE,
    valid_until DATE,
    verification_url TEXT,
    status VARCHAR(24) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_certifications_product_id ON certifications (product_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_certifications_certificate_number
    ON certifications (certificate_number);

CREATE TABLE IF NOT EXISTS favorites (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_favorite UNIQUE (user_id, product_id)
);
CREATE INDEX IF NOT EXISTS ix_favorites_user_id ON favorites (user_id);
CREATE INDEX IF NOT EXISTS ix_favorites_product_id ON favorites (product_id);

CREATE TABLE IF NOT EXISTS product_ingredients (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    original_name VARCHAR(240) NOT NULL,
    CONSTRAINT uq_product_ingredient UNIQUE (product_id, ingredient_id)
);
CREATE INDEX IF NOT EXISTS ix_product_ingredients_product_id
    ON product_ingredients (product_id);
CREATE INDEX IF NOT EXISTS ix_product_ingredients_ingredient_id
    ON product_ingredients (ingredient_id);

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    status VARCHAR(24) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_reports_user_id ON reports (user_id);
CREATE INDEX IF NOT EXISTS ix_reports_product_id ON reports (product_id);

CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    input_type VARCHAR(32) NOT NULL,
    input_value TEXT,
    extracted_text TEXT,
    halal_status VARCHAR(48) NOT NULL,
    halal_confidence INTEGER NOT NULL,
    health_status VARCHAR(24) NOT NULL,
    health_score INTEGER NOT NULL,
    result_json JSON NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_scans_user_id ON scans (user_id);
CREATE INDEX IF NOT EXISTS ix_scans_product_id ON scans (product_id);

-- Mark this schema as matching the included first Alembic migration.
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);
INSERT INTO alembic_version (version_num)
VALUES ('5aa2495de664')
ON CONFLICT (version_num) DO NOTHING;

COMMIT;
