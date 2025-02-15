from supabase import create_client, Client
import os
from functools import lru_cache

@lru_cache()
def get_supabase() -> Client:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials")
    return create_client(supabase_url, supabase_key)