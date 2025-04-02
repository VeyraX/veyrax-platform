import httpx
import json
from bs4 import BeautifulSoup
import urllib.parse
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AirbnbClient:
    BASE_URL = "https://www.airbnb.com"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    def __init__(self):
        self.session = httpx.Client(
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9",
            },
            follow_redirects=True,
            timeout=30.0
        )
    
    def _build_search_url(
        self, 
        location: str,
        place_id: Optional[str] = None,
        checkin: Optional[str] = None,
        checkout: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        pets: int = 0,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        cursor: Optional[str] = None
    ) -> str:
        search_url = f"{self.BASE_URL}/s/{urllib.parse.quote(location)}/homes"
        params = {}
        
        if place_id:
            params["place_id"] = place_id
            
        if checkin:
            params["checkin"] = checkin
            
        if checkout:
            params["checkout"] = checkout
        
        if adults > 0:
            params["adults"] = str(adults)
        
        if children > 0:
            params["children"] = str(children)
            
        if infants > 0:
            params["infants"] = str(infants)
            
        if pets > 0:
            params["pets"] = str(pets)
        
        if min_price is not None:
            params["price_min"] = str(min_price)
            
        if max_price is not None:
            params["price_max"] = str(max_price)
        
        if cursor:
            params["cursor"] = cursor
        
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            search_url = f"{search_url}?{query_string}"
            
        return search_url
    
    def _build_listing_url(
        self,
        listing_id: str,
        checkin: Optional[str] = None,
        checkout: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        pets: int = 0
    ) -> str:
        listing_url = f"{self.BASE_URL}/rooms/{listing_id}"
        params = {}
        
        if checkin:
            params["check_in"] = checkin
            
        if checkout:
            params["check_out"] = checkout
        
        if adults > 0:
            params["adults"] = str(adults)
        
        if children > 0:
            params["children"] = str(children)
            
        if infants > 0:
            params["infants"] = str(infants)
            
        if pets > 0:
            params["pets"] = str(pets)
        
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            listing_url = f"{listing_url}?{query_string}"
            
        return listing_url
    
    def search(self, **kwargs) -> Dict[str, Any]:
        location = kwargs.get("location")
        if not location:
            raise ValueError("Location is required for search")
            
        search_url = self._build_search_url(
            location=location,
            place_id=kwargs.get("place_id"),
            checkin=kwargs.get("checkin"),
            checkout=kwargs.get("checkout"),
            adults=kwargs.get("adults", 1),
            children=kwargs.get("children", 0),
            infants=kwargs.get("infants", 0),
            pets=kwargs.get("pets", 0),
            min_price=kwargs.get("min_price"),
            max_price=kwargs.get("max_price"),
            cursor=kwargs.get("cursor")
        )
        
        response = self.session.get(search_url)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        script_element = soup.select_one("#data-deferred-state-0")
        if not script_element:
            logger.warning("Could not find data-deferred-state-0 element")
            return {"search_url": search_url, "raw_data": None}
            
        client_data = json.loads(script_element.text)["niobeMinimalClientData"][0][1]
        
        return {
            "search_url": search_url,
            "raw_data": client_data
        }
    
    def get_listing_details(self, **kwargs) -> Dict[str, Any]:
        listing_id = kwargs.get("id")
        if not listing_id:
            raise ValueError("Listing ID is required")
            
        listing_url = self._build_listing_url(
            listing_id=listing_id,
            checkin=kwargs.get("checkin"),
            checkout=kwargs.get("checkout"),
            adults=kwargs.get("adults", 1),
            children=kwargs.get("children", 0),
            infants=kwargs.get("infants", 0),
            pets=kwargs.get("pets", 0)
        )
        
        
        response = self.session.get(listing_url)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        script_element = soup.select_one("#data-deferred-state-0")
        if not script_element:
            logger.warning("Could not find data-deferred-state-0 element")
            return {"listing_url": listing_url, "raw_data": None}
            
        client_data = json.loads(script_element.text)["niobeMinimalClientData"][0][1]
            
        return {
            "listing_url": listing_url,
            "raw_data": client_data
        }