from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from db.supabase import get_supabase
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
import os
import base64
import json

class TokenService:
    @staticmethod
    async def update_token(request: Request, token_data: dict, new_token_data: dict) -> dict:
        try:
            user_id = await get_user_from_request(request)
            
            supabase = get_supabase()
            result = supabase.table('users_oauth_tokens') \
                .update(new_token_data) \
                .eq('user_id', user_id) \
                .eq('provider_id', token_data['provider_id']) \
                .execute()
            
            
            if len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Token not found")
                
            return {**token_data, **new_token_data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update token: {str(e)}")

    @staticmethod
    def is_token_expired(token_data: dict) -> bool:
        if not token_data.get('expires_at'):
            return False
        
        now = datetime.now()
        expires_at = datetime.fromtimestamp(token_data['expires_at'])
        return now > expires_at

    @staticmethod
    async def get_user_token(request: Request, provider_tag: str) -> dict:
        try:
            user_id = await get_user_from_request(request)
            
            supabase = get_supabase()
            provider_res = supabase.table('providers') \
                .select('id') \
                .eq('provider_tag', provider_tag) \
                .execute()
            
            if not provider_res.data:
                raise HTTPException(status_code=404, detail="Provider not found")
                
            provider_id = provider_res.data[0]['id']
            
            token_res = supabase.table('users_oauth_tokens') \
                .select('*') \
                .eq('user_id', user_id) \
                .eq('provider_id', provider_id) \
                .execute()
            
            if not token_res.data:
                raise HTTPException(status_code=404, detail="Token not found")
                
            return token_res.data[0]
            
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get token: {str(e)}")

class GoogleTokenRefresher:
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            creds = Credentials(
                token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                scopes=token_data['scopes'].split(',')
            )
            
            creds.refresh(GoogleRequest())
            
            new_token_data = {
                'access_token': creds.token,
                'refresh_token': creds.refresh_token or token_data['refresh_token'],
                'expires_at': int(creds.expiry.timestamp()),
                'raw_token_data': {
                    'access_token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'expiry': creds.expiry.isoformat()
                }
            }
            
            return await TokenService.update_token(request, token_data, new_token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")

async def get_user_from_request(request: Request) -> str:
    try:
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
            
        access_token = auth_header.split("Bearer ")[1]
        
        payload = access_token.split('.')[1]
        decoded = base64.urlsafe_b64decode(payload + '==').decode('utf-8')
        user_data = json.loads(decoded)
        
        return user_data['sub']
        
    except Exception as e:
        print(f"[get_user_from_request] Error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    
    