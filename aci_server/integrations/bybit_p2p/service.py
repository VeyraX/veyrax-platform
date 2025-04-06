from typing import Dict, Any, List, Optional
import os
from .client import BybitP2PClient
from .schema import GetP2POffersParams
from ..common.p2p.service import BaseP2PService
from ..common.p2p.schema import P2PApiResponse

class BybitP2PService(BaseP2PService):
    def __init__(self, client: BybitP2PClient):
        super().__init__(client=client, exchange_name="bybit_p2p")
    
    def get_p2p_offers(self, params: GetP2POffersParams) -> P2PApiResponse:
        offers = super().get_p2p_offers(params) 