from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from app.core.auth.dependencies import get_current_user, get_token
from app.core.supabase_client import get_admin_client, get_user_client, get_supabase

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
async def register(body: RegisterRequest):
    admin = await get_admin_client()
    try:
        result = await admin.auth.admin.create_user({
            'email': body.email,
            'password': body.password,
            'email_confirm': True,
            'user_metadata': {'name': body.name},
        })
    except Exception as e:
        msg = str(e)
        if 'already registered' in msg.lower() or 'duplicate' in msg.lower():
            raise HTTPException(status_code=409, detail='Email already registered')
        raise HTTPException(status_code=400, detail=msg)

    auth_user = result.user
    if not auth_user:
        raise HTTPException(status_code=500, detail='Failed to create user')

    # Sync to public.users table
    now = datetime.now(timezone.utc).isoformat()
    supabase = await get_supabase()
    await supabase.table('users').upsert({
        'id': auth_user.id,
        'name': body.name,
        'email': body.email,
        'hashed_password': '',
        'created_at': now,
        'updated_at': now,
    }).execute()

    # Sign in to get a session token
    anon = await get_user_client()
    try:
        session_result = await anon.auth.sign_in_with_password({
            'email': body.email,
            'password': body.password,
        })
        access_token = session_result.session.access_token
    except Exception:
        access_token = ''

    return AuthResponse(
        access_token=access_token,
        user={
            'id': auth_user.id,
            'name': body.name,
            'email': body.email,
        },
    )


@router.post('/login')
async def login(body: LoginRequest):
    client = await get_user_client()
    try:
        result = await client.auth.sign_in_with_password({
            'email': body.email,
            'password': body.password,
        })
    except Exception as e:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    user = result.user
    session = result.session

    return AuthResponse(
        access_token=session.access_token,
        user={
            'id': user.id,
            'name': user.user_metadata.get('name', ''),
            'email': user.email,
        },
    )


@router.get('/me')
async def me(token: str = Depends(get_token)):
    client = await get_user_client(token)
    try:
        result = await client.auth.get_user()
        user = result.user
        return {
            'id': user.id,
            'name': user.user_metadata.get('name', ''),
            'email': user.email,
            'created_at': user.created_at,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail='Invalid token')
