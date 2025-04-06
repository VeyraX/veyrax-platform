from typing import Dict, Any, List, Optional
import os
from .client import BinanceP2PClient
from .schema import (
    GetP2POffersParams,
    P2POffer,
    P2POffersList,
    GetP2POffersResponse,
    ApiResponse
)
from ..common.p2p.service import BaseP2PService
from ..common.p2p.schema import P2PApiResponse
from ..common.component_handler import load_components, prepare_components_auto

class BinanceP2PService(BaseP2PService):
    def __init__(self, client: BinanceP2PClient):
        super().__init__(client=client, exchange_name="binance_p2p")
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "binance_p2p"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_p2p_offers(self, params: GetP2POffersParams) -> P2PApiResponse:
        offers = super().get_p2p_offers(params) 
        for offer in offers.data.offers:
            if offer.trade_type.lower() == "sell":
                offer.url = f"https://p2p.binance.com/trade/sell/{params.crypto}?fiat={params.fiat}&payment=all-payments"
            else:
                offer.url = f"https://p2p.binance.com/trade/all-payments/{params.crypto}?fiat={params.fiat}"
        return offers