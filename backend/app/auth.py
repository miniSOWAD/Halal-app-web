from __future__ import annotations

import asyncio
import hashlib
import hmac
import secrets
import smtplib
import uuid
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_database
from app.models import User

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user: User) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
        "type": "access",
        "exp": expires,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_reset_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "type": "password_reset",
        "exp": datetime.now(UTC) + timedelta(minutes=10),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_reset_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "password_reset":
            raise ValueError
        return uuid.UUID(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="The password reset link is invalid or expired.") from exc


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def otp_hash(email: str, purpose: str, code: str) -> str:
    value = f"{email.lower()}:{purpose}:{code}".encode()
    return hmac.new(settings.jwt_secret.encode(), value, hashlib.sha256).hexdigest()


def verify_otp_hash(email: str, purpose: str, code: str, expected: str) -> bool:
    return hmac.compare_digest(otp_hash(email, purpose, code), expected)


def _send_email_sync(to_email: str, subject: str, text: str, html: str | None = None) -> None:
    if not settings.smtp_username or not settings.smtp_password:
        raise RuntimeError("Email delivery is not configured. Add SMTP_USERNAME and SMTP_PASSWORD in FastAPI Cloud.")

    message = EmailMessage()
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)


async def send_email(to_email: str, subject: str, text: str, html: str | None = None) -> None:
    try:
        await asyncio.to_thread(_send_email_sync, to_email, subject, text, html)
    except (OSError, smtplib.SMTPException, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


async def send_otp_email(email: str, code: str, purpose: str) -> None:
    purpose_labels = {
        "REGISTER": "complete your HalalFit registration",
        "PASSWORD_RESET": "reset your HalalFit password",
        "EMAIL_CHANGE": "verify your new HalalFit email address",
    }
    action = purpose_labels.get(purpose, "verify your HalalFit email address")
    subject = f"Your HalalFit verification code: {code}"
    text = (
        f"Use code {code} to {action}. This code expires in 2 minutes. "
        "If you did not request this code, you can ignore this email."
    )
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:28px;color:#071E22">
      <div style="background:#071E22;color:white;padding:22px;border-radius:18px 18px 0 0">
        <h1 style="margin:0;font-size:24px">HalalFit</h1>
        <p style="margin:6px 0 0;color:#F4C095">Eat halal. Eat healthy.</p>
      </div>
      <div style="border:1px solid #d8e1df;border-top:0;padding:28px;border-radius:0 0 18px 18px">
        <p>Use this one-time code to {action}:</p>
        <div style="font-size:36px;font-weight:800;letter-spacing:8px;color:#1D7874;margin:22px 0">{code}</div>
        <p>This code expires in <strong>2 minutes</strong>.</p>
        <p style="color:#607273;font-size:13px">If you did not request this code, ignore this message.</p>
      </div>
    </div>
    """
    await send_email(email, subject, text, html)


async def send_contact_notification(sender: User, subject: str, category: str, message: str) -> None:
    if not settings.smtp_username or not settings.smtp_password:
        return
    text = (
        f"New HalalFit contact report\n\n"
        f"From: {sender.name} <{sender.email}>\n"
        f"Category: {category}\nSubject: {subject}\n\n{message}"
    )
    await send_email(settings.contact_receiver_email, f"HalalFit report: {subject}", text)


async def _user_from_credentials(
    credentials: HTTPAuthorizationCredentials | None,
    database: AsyncSession,
) -> User | None:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            return None
        user_id = uuid.UUID(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        return None

    result = await database.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    database: AsyncSession = Depends(get_database),
) -> User | None:
    return await _user_from_credentials(credentials, database)


async def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required.")
    return user
