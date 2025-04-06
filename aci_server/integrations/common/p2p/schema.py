from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Input schemas
class BaseP2POffersParams(BaseModel):
    fiat: str = Field(..., description="Fiat currency code (e.g., 'uah', 'usd', 'eur')")
    crypto: str = Field("usdt", description="Cryptocurrency to trade (e.g., 'usdt', 'btc', 'eth')")
    trade_type: str = Field("sell", description="Trade type: 'buy' or 'sell'")
    page: Optional[int] = Field(1, description="Page number for pagination")

# Output schemas
class Trader(BaseModel):
    nickname: str
    completion_rate: float
    orders_count: int

class P2POffer(BaseModel):
    exchange: str
    order_id: str
    trade_type: str
    price: float
    available_amount: float
    min_amount: float
    max_amount: float
    payment_methods: List[str]
    trader: Trader
    payment_timeout: int
    metadata: Dict[str, str]

class P2POffersList(BaseModel):
    offers: List[P2POffer]

class P2POffersResponse(BaseModel):
    data: P2POffersList
    message: Optional[str] = None

# API Response
class P2PApiResponse(BaseModel):
    data: Union[P2POffersList]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    ) 