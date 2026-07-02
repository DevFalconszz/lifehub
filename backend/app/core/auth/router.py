from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.auth.dependencies import get_current_user
from app.core.auth.service import create_access_token, hash_password, verify_password
from app.core.supabase_client import get_supabase

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
    supabase = await get_supabase()
    existing = await supabase.table('users').select('id').eq('email', body.email).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail='Email already registered')

    import uuid
    user_data = {
        'id': str(uuid.uuid4()),
        'name': body.name,
        'email': body.email,
        'hashed_password': hash_password(body.password),
    }
    result = await supabase.table('users').insert(user_data).execute()
    user = result.data[0]

    token = create_access_token(user['id'])
    return AuthResponse(
        access_token=token,
        user={'id': user['id'], 'name': user['name'], 'email': user['email']},
    )


@router.post('/login')
async def login(body: LoginRequest):
    supabase = await get_supabase()
    result = await supabase.table('users').select('*').eq('email', body.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    user = result.data[0]
    if not verify_password(body.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = create_access_token(user['id'])
    return AuthResponse(
        access_token=token,
        user={'id': user['id'], 'name': user['name'], 'email': user['email']},
    )


@router.get('/me')
async def me(current_user: dict = Depends(get_current_user)):
    return {
        'id': current_user['id'],
        'name': current_user['name'],
        'email': current_user['email'],
        'created_at': current_user.get('created_at', ''),
    }
