from typing import Dict, Any, List, Optional, Union, Type
import os
from .client import BaseP2PClient
from .schema import (
    BaseP2POffersParams,
    P2POffer,
    P2POffersList,
    P2POffersResponse,
    P2PApiResponse
)
from ...common.component_handler import load_components, prepare_components_auto

class BaseP2PService:
    def __init__(self, client: BaseP2PClient, exchange_name: str):
        self.client = client
        self.exchange_name = exchange_name
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Look for components in the specific exchange directory
        component_path = os.path.join(current_dir, self.exchange_name)
        return load_components(component_path)
    
    def prepare_response(self, data: Any, component_name: str = None) -> P2PApiResponse:
        tool_name = self.exchange_name
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return P2PApiResponse(data=data, component=components)
    
    def get_p2p_offers(self, params: BaseP2POffersParams) -> P2PApiResponse:
        # Get raw offers data from the client
        offers_data = self.client.get_offers(
            fiat=params.fiat,
            crypto=params.crypto,
            trade_type=params.trade_type,
            page=params.page
        )
        
        # Convert the raw data to our structured format
        offers = []
        for offer_data in offers_data:
            offer = P2POffer(
                exchange=offer_data.get("exchange", self.exchange_name),
                order_id=offer_data.get("order_id", ""),
                trade_type=offer_data.get("trade_type", ""),
                price=float(offer_data.get("price", 0)),
                available_amount=float(offer_data.get("available_amount", 0)),
                min_amount=float(offer_data.get("min_amount", 0)),
                max_amount=float(offer_data.get("max_amount", 0)),
                payment_methods=offer_data.get("payment_methods", []),
                trader=offer_data.get("trader", {"nickname": "", "completion_rate": 0, "orders_count": 0}),
                payment_timeout=int(offer_data.get("payment_timeout", 0)),
                metadata=offer_data.get("metadata", {})
            )
            offers.append(offer)
        
        # Create the response object
        offers_list = P2POffersList(offers=offers)
        
        # Return the final API response
        return self.prepare_response(offers_list, "P2POffersView") 