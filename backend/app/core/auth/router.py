from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.service import create_access_token, decode_access_token, hash_password, verify_password
from app.core.exceptions import UnauthorizedError
from app.database import get_session
from app.core.auth.models import User

router = APIRouter(prefix='/auth', tags=['auth'])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: dict


@router.post('/register')
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='Email already registered')

    user = User(name=body.name, email=body.email, hashed_password=hash_password(body.password))
    session.add(user)
    await session.flush()
    await session.refresh(user)

    token = create_access_token(str(user.id))
    return AuthResponse(
        access_token=token,
        user={'id': str(user.id), 'name': user.name, 'email': user.email},
    )


@router.post('/login')
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = create_access_token(str(user.id))
    return AuthResponse(
        access_token=token,
        user={'id': str(user.id), 'name': user.name, 'email': user.email},
    )


@router.get('/me')
async def me(current_user: User = Depends(get_current_user)):
    return {
        'id': str(current_user.id),
        'name': current_user.name,
        'email': current_user.email,
        'created_at': current_user.created_at.isoformat(),
    }
