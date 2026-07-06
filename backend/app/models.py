from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    scans: Mapped[list[Scan]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[list[Favorite]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reports: Mapped[list[Report]] = relationship(back_populates="user", cascade="all, delete-orphan")


class EmailOTP(Base):
    __tablename__ = "email_otps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), index=True)
    purpose: Mapped[str] = mapped_column(String(40), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    resend_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(220), index=True)
    brand: Mapped[str | None] = mapped_column(String(160), index=True, nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingredient_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    nutrition_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    halal_status: Mapped[str] = mapped_column(String(48), default="UNKNOWN", nullable=False)
    halal_confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    health_status: Mapped[str] = mapped_column(String(24), default="UNKNOWN", nullable=False)
    health_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_source: Mapped[str] = mapped_column(String(80), default="ADMIN", nullable=False)

    ingredients: Mapped[list[ProductIngredient]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    certifications: Mapped[list[Certification]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    scans: Mapped[list[Scan]] = relationship(back_populates="product")
    favorites: Mapped[list[Favorite]] = relationship(back_populates="product", cascade="all, delete-orphan")


class Ingredient(Base, TimestampMixin):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    e_number: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    halal_status: Mapped[str] = mapped_column(String(24), default="UNKNOWN", nullable=False)
    health_status: Mapped[str] = mapped_column(String(24), default="NEUTRAL", nullable=False)
    source_dependent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    risk_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="No explanation available.", nullable=False)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)

    products: Mapped[list[ProductIngredient]] = relationship(back_populates="ingredient")


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"
    __table_args__ = (UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), index=True)
    original_name: Mapped[str] = mapped_column(String(240))

    product: Mapped[Product] = relationship(back_populates="ingredients")
    ingredient: Mapped[Ingredient] = relationship(back_populates="products", lazy="selectin")


class HalalRule(Base, TimestampMixin):
    __tablename__ = "halal_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    keyword: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(24))
    reason: Mapped[str] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=10)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class HealthRule(Base, TimestampMixin):
    __tablename__ = "health_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nutrient: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    maximum_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    minimum_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_change: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Certification(Base, TimestampMixin):
    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    authority_name: Mapped[str] = mapped_column(String(180))
    certificate_number: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    verification_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="UNVERIFIED")

    product: Mapped[Product] = relationship(back_populates="certifications")


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True, nullable=True)
    input_type: Mapped[str] = mapped_column(String(32))
    input_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    halal_status: Mapped[str] = mapped_column(String(48), default="UNKNOWN")
    halal_confidence: Mapped[int] = mapped_column(Integer, default=0)
    health_status: Mapped[str] = mapped_column(String(24), default="UNKNOWN")
    health_score: Mapped[int] = mapped_column(Integer, default=0)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User | None] = relationship(back_populates="scans")
    product: Mapped[Product | None] = relationship(back_populates="scans", lazy="selectin")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_user_favorite"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="favorites")
    product: Mapped[Product] = relationship(back_populates="favorites", lazy="selectin")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True, nullable=True)
    subject: Mapped[str] = mapped_column(String(180), default="User report", nullable=False)
    category: Mapped[str] = mapped_column(String(40), default="GENERAL", nullable=False)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User | None] = relationship(back_populates="reports")
