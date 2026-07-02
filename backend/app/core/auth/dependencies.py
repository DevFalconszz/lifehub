from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth.service import decode_access_token
from app.core.supabase_client import get_supabase

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail='Invalid token')

    supabase = await get_supabase()
    result = await supabase.table('users').select('*').eq('id', payload.sub).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail='User not found')

    user = result.data[0]
    return user
