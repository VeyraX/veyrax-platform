from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from db.supabase import get_supabase
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
import os
import base64
import json
import requests
import aiohttp
import time
from .encryption import decrypt, encrypt, safe_decrypt, safe_encrypt, is_encrypted

class TokenService:
    @staticmethod
    async def update_token(request: Request, token_data: dict, new_token_data: dict) -> dict:
        try:
            user_id = await get_user_from_request(request)
            
            original_access_token = new_token_data.get('access_token')
            original_refresh_token = new_token_data.get('refresh_token')
            original_raw_data = None
            
            if 'raw_token_data' in new_token_data and isinstance(new_token_data['raw_token_data'], dict):
                raw_data = new_token_data['raw_token_data']
                original_raw_data = {
                    'access_token': raw_data.get('access_token'),
                    'refresh_token': raw_data.get('refresh_token')
                }
                
                if 'access_token' in raw_data:
                    raw_data['access_token'] = safe_encrypt(raw_data['access_token'])
                if 'refresh_token' in raw_data and raw_data['refresh_token']:
                    raw_data['refresh_token'] = safe_encrypt(raw_data['refresh_token'])
            
            if 'access_token' in new_token_data:
                new_token_data['access_token'] = safe_encrypt(new_token_data['access_token'])
            
            if 'refresh_token' in new_token_data and new_token_data['refresh_token']:
                new_token_data['refresh_token'] = safe_encrypt(new_token_data['refresh_token'])
            
            supabase = get_supabase()
            result = supabase.table('users_oauth_tokens') \
                .update(new_token_data) \
                .eq('user_id', user_id) \
                .eq('provider_id', token_data['provider_id']) \
                .execute()
            
            if len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Token not found")
            
            result_data = {**token_data, **new_token_data}
            
            if original_access_token:
                result_data['access_token'] = original_access_token
            if original_refresh_token:
                result_data['refresh_token'] = original_refresh_token
            
            if original_raw_data and 'raw_token_data' in result_data:
                raw_data = result_data['raw_token_data']
                if original_raw_data.get('access_token') and 'access_token' in raw_data:
                    raw_data['access_token'] = original_raw_data['access_token']
                if original_raw_data.get('refresh_token') and 'refresh_token' in raw_data:
                    raw_data['refresh_token'] = original_raw_data['refresh_token']
                
            return result_data
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
            
            token_data = token_res.data[0]
            
            if token_data.get('access_token'):
                token_data['access_token'] = safe_decrypt(token_data['access_token'])
            
            if token_data.get('refresh_token'):
                token_data['refresh_token'] = safe_decrypt(token_data['refresh_token'])
                
            if token_data.get('raw_token_data') and isinstance(token_data['raw_token_data'], dict):
                raw_data = token_data['raw_token_data']
                if 'access_token' in raw_data:
                    raw_data['access_token'] = safe_decrypt(raw_data['access_token'])
                if 'refresh_token' in raw_data and raw_data['refresh_token']:
                    raw_data['refresh_token'] = safe_decrypt(raw_data['refresh_token'])
                
            return token_data
            
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get token: {str(e)}")

class BaseTokenRefresher:
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        raise NotImplementedError("Refresh method must be implemented by subclass")

class GoogleTokenRefresher(BaseTokenRefresher):
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
            raise HTTPException(status_code=401, detail=f"Failed to refresh Google token: {str(e)}")

class ConfluenceTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            response = requests.post(
                "https://auth.atlassian.com/oauth/token",
                json={
                    "grant_type": "refresh_token",
                    "client_id": os.getenv('CONFLUENCE_CLIENT_ID'),
                    "client_secret": os.getenv('CONFLUENCE_CLIENT_SECRET'),
                    "refresh_token": token_data['refresh_token']
                }
            )
            response.raise_for_status()
            refresh_data = response.json()

            new_token_data = {
                'access_token': refresh_data['access_token'],
                'refresh_token': refresh_data.get('refresh_token', token_data['refresh_token']),
                'expires_at': int(datetime.now().timestamp() + refresh_data['expires_in']),
                'raw_token_data': refresh_data
            }
            
            return await TokenService.update_token(request, token_data, new_token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to refresh Confluence token: {str(e)}")

class JiraTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            response = requests.post(
                "https://auth.atlassian.com/oauth/token",
                json={
                    "grant_type": "refresh_token",
                    "client_id": os.getenv('JIRA_CLIENT_ID'),
                    "client_secret": os.getenv('JIRA_CLIENT_SECRET'),
                    "refresh_token": token_data['refresh_token']
                }
            )
            response.raise_for_status()
            refresh_data = response.json()

            new_token_data = {
                'access_token': refresh_data['access_token'],
                'refresh_token': refresh_data.get('refresh_token', token_data['refresh_token']),
                'expires_at': int(datetime.now().timestamp() + refresh_data['expires_in']),
                'raw_token_data': refresh_data
            }
            
            return await TokenService.update_token(request, token_data, new_token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to refresh Jira token: {str(e)}")

class OutlookTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            response = requests.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": os.getenv('OUTLOOK_CLIENT_ID'),
                    "client_secret": os.getenv('OUTLOOK_CLIENT_SECRET'),
                    "refresh_token": token_data['refresh_token'],
                    "scope": token_data['scopes']
                }
            )
            response.raise_for_status()
            refresh_data = response.json()

            new_token_data = {
                'access_token': refresh_data['access_token'],
                'refresh_token': refresh_data.get('refresh_token', token_data['refresh_token']),
                'expires_at': int(datetime.now().timestamp() + refresh_data['expires_in']),
                'raw_token_data': refresh_data
            }
            
            return await TokenService.update_token(request, token_data, new_token_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to refresh Outlook token: {str(e)}")

class DropboxTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        """Refresh Dropbox OAuth token"""
        client_id = os.getenv("DROPBOX_CLIENT_ID")
        client_secret = os.getenv("DROPBOX_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise ValueError("Missing Dropbox client credentials in environment")
            
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            raise ValueError("No refresh token available")
            
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.dropboxapi.com/oauth2/token", data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Failed to refresh token: {error_text}")
                    
                refresh_data = await response.json()
                
                new_token_data = {
                    'access_token': refresh_data['access_token'],
                    'refresh_token': refresh_data.get('refresh_token', refresh_token),
                    'expires_at': int(datetime.now().timestamp() + refresh_data.get('expires_in', 14400)),
                    'raw_token_data': refresh_data
                }
                    
                return await TokenService.update_token(request, token_data, new_token_data)

class SlackTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        if not token_data.get('refresh_token'):
            raise ValueError("No refresh token available for Slack")
            
        try:
            client_id = os.environ.get('SLACK_CLIENT_ID')
            client_secret = os.environ.get('SLACK_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                raise ValueError("Missing Slack client credentials in environment")
                
            refresh_token = token_data.get('refresh_token')
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://slack.com/api/oauth.v2.access',
                    headers=headers,
                    data=data
                ) as response:
                    result = await response.json()
                    
                    if not result.get('ok', False):
                        raise ValueError(f"Slack token refresh failed: {result.get('error', 'Unknown error')}")
                    
                    new_token_data = {
                        'access_token': result.get('access_token'),
                        'refresh_token': result.get('refresh_token', token_data.get('refresh_token')),
                        'expires_at': result.get('expires_in') 
                            and (int(time.time()) + result.get('expires_in')),
                        'scopes': token_data.get('scopes'),
                        'raw_token_data': result
                    }
                    
                    await TokenService.update_token(request, token_data, new_token_data)
                    
                    return new_token_data
                    
        except Exception as e:
            raise ValueError(f"Failed to refresh Slack token: {str(e)}")

class SentryTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            install_id = token_data.get('raw_token_data', {}).get('installation_id')
            if not install_id:
                raise ValueError("Missing installation_id in token data")

            refresh_token = token_data.get('refresh_token')
            if not refresh_token:
                raise ValueError("Missing refresh token")

            token_url = f"https://sentry.io/api/0/sentry-app-installations/{install_id}/authorizations/"
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': os.getenv('SENTRY_INTEGRATION_CLIENT_ID'),
                'client_secret': os.getenv('SENTRY_INTEGRATION_CLIENT_SECRET'),
            }

            response = requests.post(token_url, json=payload)
            response.raise_for_status()
            new_tokens = response.json()

            from datetime import datetime

            expires_at_str = new_tokens['expiresAt'].replace('Z', '+00:00')
            expires_at_dt = datetime.fromisoformat(expires_at_str)
            expires_at = int(expires_at_dt.timestamp())

            new_token_data = {
                'access_token': new_tokens['token'],
                'refresh_token': new_tokens['refreshToken'],
                'expires_at': expires_at,
                'scopes': token_data.get('scopes'),
                'raw_token_data': {
                    **token_data.get('raw_token_data', {}),
                    'installation_id': install_id
                }
            }
            
            await TokenService.update_token(request, token_data, new_token_data)
            
            return new_token_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sentry token refresh failed: {str(e)}")

class AsanaTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            refresh_token = token_data.get('refresh_token')
            if not refresh_token:
                raise ValueError("No refresh token available")
                
            client_id = os.getenv('ASANA_CLIENT_ID')
            client_secret = os.getenv('ASANA_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                raise ValueError("Missing Asana client credentials")
                
            token_url = "https://app.asana.com/-/oauth_token"
            payload = {
                'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Failed to refresh token: {error_text}")
                        
                    token_response = await response.json()
                    
            new_token_data = {
                'access_token': token_response.get('access_token'),
                'refresh_token': token_response.get('refresh_token', refresh_token),
                'expires_at': int(time.time()) + token_response.get('expires_in', 3600),
                'raw_token_data': token_response
            }
            
            return await TokenService.update_token(request, token_data, new_token_data)
            
        except Exception as e:
            print(f"Error refreshing Asana token: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")

class FigmaTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            refresh_token = token_data.get('refresh_token')
            if not refresh_token:
                raise ValueError("No refresh token available")
                
            client_id = os.getenv('FIGMA_CLIENT_ID')
            client_secret = os.getenv('FIGMA_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                raise ValueError("Missing Figma client credentials")
                
            token_url = "https://www.figma.com/api/oauth/token"
            payload = {
                'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Failed to refresh token: {error_text}")
                        
                    token_response = await response.json()
                    
            new_token_data = {
                'access_token': token_response.get('access_token'),
                'refresh_token': token_response.get('refresh_token', refresh_token),
                'expires_at': int(time.time()) + token_response.get('expires_in', 3600),
                'raw_token_data': token_response
            }
            
            return await TokenService.update_token(request, token_data, new_token_data)
            
        except Exception as e:
            print(f"Error refreshing Figma token: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")

class RedditTokenRefresher(BaseTokenRefresher):
    @staticmethod
    async def refresh(request: Request, token_data: dict) -> dict:
        try:
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                raise ValueError("Missing Reddit client credentials")
            
            refresh_token = token_data.get('refresh_token')
            if not refresh_token:
                raise ValueError("No refresh token available")

            auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://www.reddit.com/api/v1/access_token",
                    headers=headers,
                    data=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Failed to refresh token: {error_text}")
                    
                    refresh_data = await response.json()
                    
                    new_token_data = {
                        'access_token': refresh_data['access_token'],
                        'refresh_token': refresh_token, 
                        'expires_at': int(time.time() + refresh_data['expires_in']),
                        'raw_token_data': refresh_data
                    }
                    
                    return await TokenService.update_token(request, token_data, new_token_data)
                    
        except Exception as e:
            raise HTTPException(
                status_code=401, 
                detail=f"Failed to refresh Reddit token: {str(e)}"
            )

class TokenRefresherFactory:
    _refreshers = {
        'google': GoogleTokenRefresher,
        'confluence': ConfluenceTokenRefresher,
        'jira': JiraTokenRefresher,
        'outlook': OutlookTokenRefresher,
        'dropbox': DropboxTokenRefresher,
        'slack': SlackTokenRefresher,
        'asana': AsanaTokenRefresher,
        'figma': FigmaTokenRefresher,
        "sentry": SentryTokenRefresher,
        "reddit": RedditTokenRefresher,
    }

    @classmethod
    def get_refresher(cls, provider_tag: str) -> BaseTokenRefresher:
        refresher = cls._refreshers.get(provider_tag)
        if not refresher:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider_tag}")
        return refresher

async def get_user_from_request(request: Request) -> str:
    try:
        api_key = request.headers.get("VEYRAX_API_KEY")
        if api_key:
            supabase = get_supabase()
            result = supabase.table('users_api_keys') \
                .select('user_id') \
                .eq('api_key', api_key) \
                .execute()
                
            if not result.data:
                raise HTTPException(status_code=401, detail="Invalid API key")
                
            return result.data[0]['user_id']
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing authorization header")
            
        if auth_header.startswith("Bearer "):
            access_token = auth_header.split("Bearer ")[1]
            payload = access_token.split('.')[1]
            decoded = base64.urlsafe_b64decode(payload + '==').decode('utf-8')
            user_data = json.loads(decoded)
            return user_data['sub']
        else:
            raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>' or provide 'VEYRAX_API_KEY' header")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")

async def get_custom_base_url(request: Request, provider_tag: str) -> str:
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

        base_url_res = supabase.table('users_provider_api_keys') \
            .select('raw_data') \
            .eq('user_id', user_id) \
            .eq('provider_id', provider_id) \
            .execute()
        
        if not base_url_res.data:
            return None 
            
        raw_data = base_url_res.data[0].get('raw_data', {})
        raw_data = json.loads(raw_data)
                
        base_url = raw_data.get('base_url')
        
        return base_url     
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get custom base URL: {str(e)}")

async def validate_provider_api_key(request: Request, provider_tag: str) -> str:
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
        
        api_key_res = supabase.table('users_provider_api_keys') \
            .select('api_key') \
            .eq('user_id', user_id) \
            .eq('provider_id', provider_id) \
            .execute()
        
        if not api_key_res.data:
            raise HTTPException(status_code=404, detail=f"API key for provider {provider_tag} not found")
        
        encrypted_api_key = api_key_res.data[0]['api_key']
        decrypted_api_key = safe_decrypt(encrypted_api_key)
            
        return decrypted_api_key
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate provider API key: {str(e)}")

async def get_user_db_credentials(request: Request, provider_tag: str) -> dict:
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
        
        creds_res = supabase.table('users_db_access') \
            .select('credentials') \
            .eq('user_id', user_id) \
            .eq('provider_id', provider_id) \
            .execute()
        
        if not creds_res.data:
            raise HTTPException(status_code=404, detail="Database credentials not found")
        
        credentials = json.loads(creds_res.data[0]['credentials'])
        
        if credentials.get('password'):
            credentials['password'] = safe_decrypt(credentials['password'])
        
        return credentials
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database credentials: {str(e)}")

async def get_provider_custom_auth(request: Request, provider_tag: str) -> dict:
    try:
        user_id = await get_user_from_request(request)
        
        supabase = get_supabase()
        provider_res = supabase.table('providers') \
            .select('id, auth_schema') \
            .eq('provider_tag', provider_tag) \
            .execute()
        
        if not provider_res.data:
            raise HTTPException(status_code=404, detail="Provider not found")
            
        provider_id = provider_res.data[0]['id']
        auth_schema = provider_res.data[0].get('auth_schema', [])
        
        auth_res = supabase.table('user_provider_custom_auth') \
            .select('raw_data') \
            .eq('user_id', user_id) \
            .eq('provider_id', provider_id) \
            .execute()
        
        if not auth_res.data:
            raise HTTPException(status_code=404, detail=f"Custom auth data for provider {provider_tag} not found")
        
        raw_data = json.loads(auth_res.data[0]['raw_data']) if isinstance(auth_res.data[0]['raw_data'], str) else auth_res.data[0]['raw_data']
        
        # Decrypt sensitive fields
        for field in auth_schema:
            field_key = field.get('key')
            is_sensitive = field.get('type') == 'password' or field.get('sensitive', False)
            
            if is_sensitive and field_key in raw_data and raw_data[field_key]:
                if is_encrypted(raw_data[field_key]):
                    raw_data[field_key] = safe_decrypt(raw_data[field_key])
        
        return raw_data
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider custom auth: {str(e)}")

async def update_provider_custom_auth(request: Request, provider_tag: str, auth_data: dict) -> dict:
    try:
        user_id = await get_user_from_request(request)
        
        supabase = get_supabase()
        provider_res = supabase.table('providers') \
            .select('id, auth_schema') \
            .eq('provider_tag', provider_tag) \
            .execute()
        
        if not provider_res.data:
            raise HTTPException(status_code=404, detail="Provider not found")
            
        provider_id = provider_res.data[0]['id']
        auth_schema = provider_res.data[0].get('auth_schema', [])
        
        # Create a copy of auth_data to avoid modifying the original
        encrypted_auth_data = auth_data.copy()
        original_values = {}
        
        # Encrypt sensitive fields
        for field in auth_schema:
            field_key = field.get('key')
            is_sensitive = field.get('type') == 'password' or field.get('sensitive', False)
            
            if is_sensitive and field_key in encrypted_auth_data and encrypted_auth_data[field_key]:
                original_values[field_key] = encrypted_auth_data[field_key]
                encrypted_auth_data[field_key] = safe_encrypt(encrypted_auth_data[field_key])
        
        # Check if the record exists
        check_res = supabase.table('user_provider_custom_auth') \
            .select('id') \
            .eq('user_id', user_id) \
            .eq('provider_id', provider_id) \
            .execute()
        
        if check_res.data:
            # Update existing record
            result = supabase.table('user_provider_custom_auth') \
                .update({'raw_data': encrypted_auth_data}) \
                .eq('user_id', user_id) \
                .eq('provider_id', provider_id) \
                .execute()
        else:
            # Create new record
            result = supabase.table('user_provider_custom_auth') \
                .insert({
                    'user_id': user_id,
                    'provider_id': provider_id,
                    'raw_data': encrypted_auth_data
                }) \
                .execute()
        
        # Restore original values for return
        result_data = encrypted_auth_data.copy()
        for key, value in original_values.items():
            result_data[key] = value
            
        return result_data
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update provider custom auth: {str(e)}")