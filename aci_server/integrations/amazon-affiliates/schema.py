from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import validator

# Base models
class AmazonSearchParam(BaseModel):
    keyword: str

class AmazonSearchItem(BaseModel):
    title: str
    description: str
    image_url: str
    feedback_count: str
    rating: str
    price: str
    url: str

class AmazonSearchResponse(BaseModel):
    items: List[AmazonSearchItem]
    
class ApiResponse(BaseModel):
    data: Union[
        AmazonSearchResponse
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None