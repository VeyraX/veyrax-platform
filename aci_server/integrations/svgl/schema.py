from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union

# Input schemas
class GetAllSvgsParams(BaseModel):
    limit: Optional[int] = Field(
        None, 
        ge=1, 
        description="Limit the number of SVGs returned"
    )

class GetSvgByCategoryParams(BaseModel):
    category: str = Field(
        ...,
        description="Category name to filter SVGs by"
    )

class SearchSvgsParams(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Search query to find SVGs by name"
    )

# Output schemas
class ThemeOptions(BaseModel):
    light: HttpUrl
    dark: HttpUrl

class Svg(BaseModel):
    id: Optional[int] = None
    title: str
    category: Union[str, List[str]]
    route: Union[HttpUrl, ThemeOptions]
    wordmark: Optional[Union[HttpUrl, ThemeOptions]] = None
    brandUrl: Optional[HttpUrl] = None
    url: HttpUrl

class SvgsList(BaseModel):
    items: List[Svg]

class Category(BaseModel):
    category: str
    total: int

class CategoriesList(BaseModel):
    items: List[Category]

# Response model
class ApiResponse(BaseModel):
    data: Union[SvgsList, CategoriesList, Svg]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )