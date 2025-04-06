import requests
from typing import Dict, Any, List, Optional
from ..common.p2p.client import BaseP2PClient

class BinanceP2PClient(BaseP2PClient):
    BASE_URL = "https://p2p-binance-api-p2p-okx-api-and-p2p-bybit-real-time-data.p.rapidapi.com"
    EXCHANGE = "binance"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-rapidapi-host": "p2p-binance-api-p2p-okx-api-and-p2p-bybit-real-time-data.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }

    def get_endpoint_prefix(self, trade_type: str) -> str:
        """
        Get the endpoint prefix based on trade type.
        For Binance, "buy" means the user wants to buy crypto (so API needs "binance_sell")
        and "sell" means the user wants to sell crypto (so API needs "binance_buy").
        """
        if trade_type.lower() == "sell":
            return "binance_buy"
        else:  # trade_type == "buy"
            return "binance_sell"

    def get_offers(self, fiat: str, crypto: str = "usdt", trade_type: str = "sell", page: int = 1) -> List[Dict[str, Any]]:
        """Get P2P offers from Binance"""
        endpoint_suffix = self.get_endpoint_prefix(trade_type)
        
        endpoint = f"{self.BASE_URL}/{endpoint_suffix}/{crypto}"
        params = {
            "fiat": fiat.lower(),
            "page": page
        }
        
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def validate_api_key(self) -> bool:
        """Validate the API key by making a simple request"""
        try:
            # Just try to get the first page of USDT/USD offers to validate the key
            self.get_offers(fiat="usd", page=1)
            return True
        except Exception:
            return False 