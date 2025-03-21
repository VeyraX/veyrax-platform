from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import validator

# Input params
class AmazonSearchParam(BaseModel):
    keyword: str

class AmazonGetItemsParam(BaseModel):
    asins: Union[str, List[str]]

class AmazonGetVariationsParam(BaseModel):
    asin: str

class AmazonGetBrowseNodesParam(BaseModel):
    browse_node_ids: List[str]

class AmazonGetAsinParam(BaseModel):
    url: str

# Output models
class AmazonImage(BaseModel):
    small: Optional[str] = None
    medium: Optional[str] = None
    large: Optional[str] = None

class AmazonPrice(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    display_amount: str

class AmazonRating(BaseModel):
    value: Optional[float] = None
    count: Optional[int] = None

class AmazonSearchItem(BaseModel):
    asin: str
    title: str
    description: str
    image_url: str
    feedback_count: str
    rating: str
    price: str
    url: str

class AmazonItemDetail(BaseModel):
    asin: str
    title: str
    description: Optional[str] = None
    brand: Optional[str] = None
    images: Optional[AmazonImage] = None
    price: Optional[AmazonPrice] = None
    rating: Optional[AmazonRating] = None
    url: str
    available: Optional[bool] = None
    features: Optional[List[str]] = None
    color: Optional[str] = None

class AmazonBrowseNode(BaseModel):
    id: str
    display_name: str
    context_free_name: Optional[str] = None
    is_root: Optional[bool] = None
    ancestor: Optional[Dict[str, Any]] = None
    children: Optional[List[Dict[str, Any]]] = None

# Response models
class AmazonSearchResponse(BaseModel):
    items: List[AmazonSearchItem]

class AmazonItemsResponse(BaseModel):
    items: List[AmazonItemDetail]

class AmazonVariationsResponse(BaseModel):
    items: List[AmazonItemDetail]
    variation_summary: Optional[Dict[str, Any]] = None

class AmazonBrowseNodesResponse(BaseModel):
    nodes: List[AmazonBrowseNode]

class AmazonAsinResponse(BaseModel):
    asin: str

class ApiResponse(BaseModel):
    data: Union[
        AmazonSearchResponse,
        AmazonItemsResponse,
        AmazonVariationsResponse,
        AmazonBrowseNodesResponse,
        AmazonAsinResponse,
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None