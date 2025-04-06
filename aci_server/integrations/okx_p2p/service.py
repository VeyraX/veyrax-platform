from typing import Dict, Any, List, Optional
import os
from .client import OkxP2PClient
from .schema import GetP2POffersParams
from ..common.p2p.service import BaseP2PService
from ..common.p2p.schema import P2PApiResponse

class OkxP2PService(BaseP2PService):
    """Service for interacting with OKX P2P marketplace"""
    
    def __init__(self, client: OkxP2PClient):
        """Initialize the service with the OKX P2P client"""
        super().__init__(client=client, exchange_name="okx_p2p")
        
    def get_p2p_offers(self, params: GetP2POffersParams) -> P2PApiResponse:
        """
        Get P2P offers from OKX P2P marketplace.
        
        Args:
            params: Parameters for the request
            
        Returns:
            P2PApiResponse: API response containing the offers
        """
        return super().get_p2p_offers(params) 