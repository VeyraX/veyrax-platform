from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from ..common.p2p.schema import (
    BaseP2POffersParams,
    P2POffer,
    P2POffersList,
    P2POffersResponse,
    P2PApiResponse,
    Trader
)

# Input schemas
class GetP2POffersParams(BaseP2POffersParams):
    pass  # All fields are inherited from the base class 

# Output schemas - reuse from common p2p
GetP2POffersResponse = P2POffersResponse

# API Response
ApiResponse = P2PApiResponse 