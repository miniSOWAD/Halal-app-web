import uuid
from datetime import datetime, timedelta, timezone

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
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
        "exp": expires,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def _user_from_credentials(
    credentials: HTTPAuthorizationCredentials | None,
    database: AsyncSession,
) -> User | None:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    database: AsyncSession = Depends(get_database),
) -> User:
    user = await _user_from_credentials(credentials, database)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return user
