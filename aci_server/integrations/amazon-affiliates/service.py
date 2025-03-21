
from typing import Optional, List, Dict, Any, Union
from .client import AmazonClient
from .schema import (
    ApiResponse,
    AmazonSearchResponse,
    AmazonSearchItem
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class AmazonService:
    def __init__(self, client: AmazonClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "asana"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def search_items(self, keyword: str):
            search_results = self.client.search_items(keyword)
            items = []
            for item in search_results.items:
                payload = {
                    "title": item.item_info.title.display_value if item.item_info.title else "No Title",
                    "description": (
                        item.item_info.features.display_values[0]
                        if item.item_info.features and item.item_info.features.display_values else "No Description"
                    ),
                    "image_url": (
                        item.images.primary.large.url
                        if item.images and item.images.primary and item.images.primary.large else "No Image"
                    ),
                    "feedback_count": (
                        item.offers.listings[0].merchant_info.feedback_count
                        if item.offers and item.offers.listings else "N/A"
                    ),
                    "rating": (
                        item.offers.listings[0].merchant_info.feedback_rating
                        if item.offers and item.offers.listings else "N/A"
                    ),
                    "price": (
                        item.offers.listings[0].price.display_amount
                        if item.offers and item.offers.listings else "No Price Available"
                    ),
                    "url": item.detail_page_url
                }
                {
                    "title": item.item_info.title.display_value if item.item_info.title else "No Title",
                    "description": (
                        item.item_info.features.display_values[0]
                        if item.item_info.features and item.item_info.features.display_values else "No Description"
                    ),
                    "image_url": (
                        item.images.primary.large.url
                        if item.images and item.images.primary and item.images.primary.large else "No Image"
                    ),
                    "feedback_count": (
                        item.offers.listings[0].merchant_info.feedback_count
                        if item.offers and item.offers.listings else "N/A"
                    ),
                    "rating": (
                        item.offers.listings[0].merchant_info.feedback_rating
                        if item.offers and item.offers.listings else "N/A"
                    ),
                    "price": (
                        item.offers.listings[0].price.display_amount
                        if item.offers and item.offers.listings else "No Price Available"
                    ),
                    "url": item.detail_page_url
                }
                casted_item = AmazonSearchItem(**payload)
                items.append(casted_item)
            
            return AmazonSearchResponse(items=items)