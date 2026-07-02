from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return credentials.credentials


async def get_current_user(token: str = Depends(get_token)) -> dict:
    from app.core.supabase_client import get_user_client
    client = await get_user_client(token)
    try:
        result = await client.auth.get_user()
        user = result.user
        return {
            'id': user.id,
            'name': user.user_metadata.get('name', ''),
            'email': user.email,
        }
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')
