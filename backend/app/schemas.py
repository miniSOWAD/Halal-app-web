from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

HalalStatus = Literal[
    "CERTIFIED_HALAL",
    "NO_PROHIBITED_INGREDIENT_FOUND",
    "HARAM",
    "DOUBTFUL",
    "UNKNOWN",
]
HealthStatus = Literal["HEALTHY", "MODERATE", "UNHEALTHY", "UNKNOWN"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    phone: str | None = Field(default=None, max_length=32)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    phone: str | None = Field(default=None, max_length=32)


class PasswordChange(BaseModel):
    old_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class EmailChangeRequest(BaseModel):
    new_email: EmailStr


class EmailChangeVerify(BaseModel):
    new_email: EmailStr
    otp: str = Field(pattern=r"^\d{6}$")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    country: str | None
    phone: str | None
    email_verified: bool
    is_admin: bool
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class OTPResponse(BaseModel):
    message: str
    email: EmailStr
    expires_in_seconds: int = 120
    resend_in_seconds: int = 60


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(pattern=r"^\d{6}$")


class PasswordResetToken(BaseModel):
    reset_token: str
    expires_in_seconds: int = 600


class PasswordReset(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class IngredientCreate(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    e_number: str | None = None
    halal_status: str = "UNKNOWN"
    health_status: str = "NEUTRAL"
    source_dependent: bool = False
    risk_level: int = Field(default=0, ge=0, le=5)
    explanation: str
    source: str | None = None


class IngredientUpdate(BaseModel):
    name: str | None = None
    aliases: list[str] | None = None
    e_number: str | None = None
    halal_status: str | None = None
    health_status: str | None = None
    source_dependent: bool | None = None
    risk_level: int | None = Field(default=None, ge=0, le=5)
    explanation: str | None = None
    source: str | None = None


class IngredientResponse(IngredientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class CertificationCreate(BaseModel):
    product_id: uuid.UUID
    authority_name: str
    certificate_number: str
    country: str | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    verification_url: str | None = None
    status: str = "UNVERIFIED"


class CertificationResponse(CertificationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=220)
    brand: str | None = Field(default=None, max_length=160)
    category: str | None = Field(default=None, max_length=120)
    barcode: str | None = Field(default=None, max_length=32)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    image_url: str | None = None
    ingredient_text: str | None = None
    nutrition_data: dict[str, Any] = Field(default_factory=dict)
    data_source: str = "ADMIN"


class ProductUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    category: str | None = None
    barcode: str | None = None
    country: str | None = None
    image_url: str | None = None
    ingredient_text: str | None = None
    nutrition_data: dict[str, Any] | None = None


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    brand: str | None
    category: str | None
    barcode: str | None
    image_url: str | None
    halal_status: str
    halal_confidence: int
    health_status: str
    health_score: int


class ProductResponse(ProductSummary):
    country: str | None
    ingredient_text: str | None
    nutrition_data: dict[str, Any]
    explanation: str | None
    data_source: str
    certifications: list[CertificationResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class IngredientCheckRequest(BaseModel):
    ingredient_text: str = Field(min_length=2, max_length=20_000)
    nutrition_data: dict[str, Any] | None = None
    product_name: str | None = None
    country: str | None = None


class CodeScanRequest(BaseModel):
    code: str = Field(min_length=1, max_length=2_000)
    format: str = "UNKNOWN"
    country: str | None = None


class RiskyIngredient(BaseModel):
    name: str
    status: str
    reason: str
    matched_name: str | None = None


class IngredientResult(BaseModel):
    name: str
    status: str
    health_status: str
    reason: str
    matched: bool


class CertificateResult(BaseModel):
    found: bool
    status: str = "UNVERIFIED"
    authority: str | None = None
    certificate_number: str | None = None
    valid_until: date | None = None
    verification_url: str | None = None


class HalalResult(BaseModel):
    status: HalalStatus
    label: str
    confidence: int = Field(ge=0, le=100)
    reasons: list[str]
    risky_ingredients: list[RiskyIngredient]
    certificate: CertificateResult


class HealthResult(BaseModel):
    status: HealthStatus
    score: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    reasons: list[str]


class AnalysisProduct(BaseModel):
    id: uuid.UUID | None = None
    name: str
    brand: str | None = None
    barcode: str | None = None
    image_url: str | None = None


class AlternativeProduct(BaseModel):
    id: uuid.UUID
    name: str
    brand: str | None = None
    image_url: str | None = None
    health_score: int
    halal_status: str


class AnalysisResponse(BaseModel):
    scan_id: uuid.UUID
    input_type: str
    product: AnalysisProduct | None
    extracted_text: str | None = None
    ingredients: list[IngredientResult]
    halal: HalalResult
    health: HealthResult
    recommendation: str
    alternatives: list[AlternativeProduct] = Field(default_factory=list)
    created_at: datetime


class ScanHistoryItem(BaseModel):
    id: uuid.UUID
    input_type: str
    product: ProductSummary | None
    halal_status: str
    halal_confidence: int
    health_status: str
    health_score: int
    created_at: datetime


class ReportCreate(BaseModel):
    product_id: uuid.UUID | None = None
    subject: str = Field(default="User report", min_length=3, max_length=180)
    category: Literal["GENERAL", "PRODUCT_DATA", "TECHNICAL", "ACCOUNT", "OTHER"] = "GENERAL"
    message: str = Field(min_length=5, max_length=4_000)


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID | None
    subject: str
    category: str
    message: str
    status: str
    created_at: datetime


class ReportUpdate(BaseModel):
    status: Literal["OPEN", "REVIEWING", "RESOLVED", "REJECTED"]


class AdminDashboard(BaseModel):
    users: int
    products: int
    ingredients: int
    scans: int
    open_reports: int
