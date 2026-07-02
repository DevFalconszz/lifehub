from app.core.supabase_client import get_supabase, close_supabase


async def get_session():
    return await get_supabase()
