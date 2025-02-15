from pydantic import BaseModel

class UserOAuthTokens(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    expires_at: int
    scope: str
    