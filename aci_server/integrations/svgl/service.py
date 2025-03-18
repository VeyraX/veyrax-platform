from typing import List, Dict, Any, Optional
import os
from .client import SvglClient
from .schema import (
    SvgsList, 
    CategoriesList, 
    Svg,
    Category,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class SvglService:
    def __init__(self, client: SvglClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "svgl"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def get_all_svgs(self, limit: Optional[int] = None) -> ApiResponse:
        """Get all SVGs with optional limit"""
        response = self.client.get_all_svgs(limit)
        svg_list = [Svg.model_validate(svg) for svg in response]
        svgs_list = SvgsList(items=svg_list)
        return self.prepare_response(svgs_list, "SvglIconsGrid")

    def get_svg_by_category(self, category: str) -> ApiResponse:
        """Get SVGs filtered by category"""
        response = self.client.get_svg_by_category(category)
        svg_list = [Svg.model_validate(svg) for svg in response]
        svgs_list = SvgsList(items=svg_list)
        return self.prepare_response(svgs_list, "SvglIconsGrid")

    def get_categories(self) -> ApiResponse:
        """Get all available categories with counts"""
        response = self.client.get_categories()
        category_list = [Category.model_validate(category) for category in response]
        categories_list = CategoriesList(items=category_list)
        return self.prepare_response(categories_list, "SvglCategoriesCard")

    def search_svgs(self, query: str) -> ApiResponse:
        """Search SVGs by name"""
        response = self.client.search_svgs(query)
        svg_list = [Svg.model_validate(svg) for svg in response]
        svgs_list = SvgsList(items=svg_list)
        return self.prepare_response(svgs_list, "SvglIconsGrid")
