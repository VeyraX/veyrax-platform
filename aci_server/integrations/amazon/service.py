from typing import Optional, List, Dict, Any, Union
from .client import AmazonClient
from .schema import (
    ApiResponse,
    AmazonSearchResponse,
    AmazonSearchItem,
    AmazonSearchParam,
    AmazonGetItemsParam,
    AmazonGetVariationsParam,
    AmazonGetBrowseNodesParam,
    AmazonGetAsinParam,
    AmazonItemsResponse,
    AmazonItemDetail,
    AmazonVariationsResponse,
    AmazonBrowseNodesResponse,
    AmazonBrowseNode,
    AmazonAsinResponse,
    AmazonImage,
    AmazonPrice,
    AmazonRating
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
        tool_name = "amazon"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def search_items(self, params: AmazonSearchParam) -> ApiResponse:
        search_results = self.client.search_items(params.keyword)
        items = []
        
        for item in search_results.items:
            payload = {
                "asin": getattr(item, "asin", ""),
                "title": self._get_title(item),
                "description": self._get_description(item),
                "image_url": self._get_image_url(item),
                "feedback_count": self._get_feedback_count(item),
                "rating": self._get_rating(item),
                "price": self._get_price(item),
                "url": getattr(item, "detail_page_url", "#")
            }
            casted_item = AmazonSearchItem(**payload)
            items.append(casted_item)
        
        response = AmazonSearchResponse(items=items)
        return self.prepare_response(response)
    
    def get_items(self, params: AmazonGetItemsParam) -> ApiResponse:
        result = self.client.get_items(params.asins)
        items = []
        
        # Handle single item response
        if not isinstance(result, list):
            result = [result]
            
        for item in result:
            if not item:
                continue
                
            item_detail = self._convert_to_item_detail(item)
            items.append(item_detail)
            
        response = AmazonItemsResponse(items=items)
        return self.prepare_response(response)
    
    def get_variations(self, params: AmazonGetVariationsParam) -> ApiResponse:
        variations = self.client.get_variations(params.asin)
        items = []
        
        for item in variations.items:
            if not item:
                continue
                
            item_detail = self._convert_to_item_detail(item)
            items.append(item_detail)
        
        variation_summary = {}
        if hasattr(variations, "variation_summary"):
            summary = variations.variation_summary
            # Convert complex variation_summary object to a simple dictionary
            variation_summary = {
                "page_count": getattr(summary, "page_count", None),
                "variation_count": getattr(summary, "variation_count", None),
                "price": getattr(summary, "price", None)
            }
            
            # Handle variation dimensions separately as they're complex objects
            if hasattr(summary, "variation_dimensions"):
                dimensions = []
                for dim in summary.variation_dimensions:
                    dimension = {
                        "name": getattr(dim, "name", ""),
                        "display_name": getattr(dim, "display_name", ""),
                        "values": getattr(dim, "values", [])
                    }
                    dimensions.append(dimension)
                variation_summary["variation_dimensions"] = dimensions
            
        response = AmazonVariationsResponse(
            items=items,
            variation_summary=variation_summary
        )
        return self.prepare_response(response)
    
    def get_browse_nodes(self, params: AmazonGetBrowseNodesParam) -> ApiResponse:
        browse_nodes_result = self.client.get_browse_nodes(params.browse_node_ids)
        nodes = []
        
        for node in browse_nodes_result:
            if not node:
                continue
                
            node_data = {
                "id": getattr(node, "id", ""),
                "display_name": getattr(node, "display_name", ""),
                "context_free_name": getattr(node, "context_free_name", None),
                "is_root": getattr(node, "is_root", None),
                "ancestor": getattr(node, "ancestor", None),
                "children": getattr(node, "children", None)
            }
            
            node_obj = AmazonBrowseNode(**node_data)
            nodes.append(node_obj)
            
        response = AmazonBrowseNodesResponse(nodes=nodes)
        return self.prepare_response(response)
    
    def get_asin_from_url(self, params: AmazonGetAsinParam) -> ApiResponse:
        asin = self.client.get_asin_from_url(params.url)
        response = AmazonAsinResponse(asin=asin)
        return self.prepare_response(response)
    
    def _convert_to_item_detail(self, item) -> AmazonItemDetail:
        images = None
        if hasattr(item, "images") and item.images and hasattr(item.images, "primary"):
            images = AmazonImage(
                small=getattr(item.images.primary.small, "url", None) if hasattr(item.images.primary, "small") else None,
                medium=getattr(item.images.primary.medium, "url", None) if hasattr(item.images.primary, "medium") else None,
                large=getattr(item.images.primary.large, "url", None) if hasattr(item.images.primary, "large") else None
            )
            
        price = None
        if (hasattr(item, "offers") and item.offers and 
            hasattr(item.offers, "listings") and len(item.offers.listings) > 0):
            price_obj = item.offers.listings[0].price
            price = AmazonPrice(
                amount=getattr(price_obj, "amount", None),
                currency=getattr(price_obj, "currency", None),
                display_amount=getattr(price_obj, "display_amount", "N/A")
            )
            
        rating = None
        if hasattr(item, "item_info") and hasattr(item.item_info, "by_line_info"):
            rating = AmazonRating(
                value=getattr(item.item_info.by_line_info, "rating", None),
                count=getattr(item.item_info.by_line_info, "rating_count", None)
            )
        
        features = []
        if (hasattr(item, "item_info") and hasattr(item.item_info, "features") and 
            hasattr(item.item_info.features, "display_values")):
            features = item.item_info.features.display_values
            
        # Extract brand from its display_value if it's an object
        brand = None
        if hasattr(item, "item_info") and hasattr(item.item_info, "by_line_info"):
            brand_info = getattr(item.item_info.by_line_info, "brand", None)
            if brand_info:
                if isinstance(brand_info, str):
                    brand = brand_info
                elif hasattr(brand_info, "display_value"):
                    brand = brand_info.display_value
                
        # Extract color from its display_value if it's an object
        color = None
        if hasattr(item, "item_info") and hasattr(item.item_info, "product_info"):
            color_info = getattr(item.item_info.product_info, "color", None)
            if color_info:
                if isinstance(color_info, str):
                    color = color_info
                elif hasattr(color_info, "display_value"):
                    color = color_info.display_value
            
        return AmazonItemDetail(
            asin=getattr(item, "asin", ""),
            title=self._get_title(item),
            description=self._get_description(item),
            brand=brand,
            images=images,
            price=price,
            rating=rating,
            url=getattr(item, "detail_page_url", "#"),
            available=getattr(item, "offers.listings[0].availability.type", None) == "NOW" if hasattr(item, "offers") and hasattr(item.offers, "listings") and len(item.offers.listings) > 0 else None,
            features=features,
            color=color
        )
    
    def _get_title(self, item):
        if hasattr(item, "item_info") and hasattr(item.item_info, "title"):
            return getattr(item.item_info.title, "display_value", "No Title")
        return "No Title"
    
    def _get_description(self, item):
        if (hasattr(item, "item_info") and hasattr(item.item_info, "features") and 
            hasattr(item.item_info.features, "display_values") and len(item.item_info.features.display_values) > 0):
            return item.item_info.features.display_values[0]
        return "No Description"
    
    def _get_image_url(self, item):
        if (hasattr(item, "images") and hasattr(item.images, "primary") and 
            hasattr(item.images.primary, "large")):
            return getattr(item.images.primary.large, "url", "No Image")
        return "No Image"
    
    def _get_feedback_count(self, item):
        if (hasattr(item, "offers") and hasattr(item.offers, "listings") and 
            len(item.offers.listings) > 0 and hasattr(item.offers.listings[0], "merchant_info")):
            feedback_count = getattr(item.offers.listings[0].merchant_info, "feedback_count", "N/A")
            return str(feedback_count) if feedback_count != "N/A" else feedback_count
        return "N/A"
    
    def _get_rating(self, item):
        if (hasattr(item, "offers") and hasattr(item.offers, "listings") and 
            len(item.offers.listings) > 0 and hasattr(item.offers.listings[0], "merchant_info")):
            rating = getattr(item.offers.listings[0].merchant_info, "feedback_rating", "N/A")
            return str(rating) if rating != "N/A" else rating
        return "N/A"
    
    def _get_price(self, item):
        if (hasattr(item, "offers") and hasattr(item.offers, "listings") and 
            len(item.offers.listings) > 0 and hasattr(item.offers.listings[0], "price")):
            return getattr(item.offers.listings[0].price, "display_amount", "No Price Available")
        return "No Price Available"