from typing import Optional, Dict, Any, List
from .client import BraveClient
from .schema import (
    WebSearchApiResponse, 
    ApiResponse, 
    WebSearchParams, 
    ImageSearchParams, 
    VideoSearchParams, 
    NewsSearchParams, 
    ImageSearchResult, 
    VideoSearchResult,
    NewsSearchResult
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class BraveService:
    def __init__(self, client: BraveClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "brave"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def web_search(self, params: WebSearchParams) -> ApiResponse:
        """Perform a web search and format response"""
        processed_params = self._process_web_params(params)
        print("web_search processed_params", processed_params)
        response = self.client.web_search(processed_params)
        print("web_search response", response)
        validated = WebSearchApiResponse(**response)
        return self.prepare_response(validated, None)

    def _process_web_params(self, params: WebSearchParams) -> Dict[str, Any]:
        """Convert Pydantic model to API parameters"""
        params_dict = params.model_dump(exclude_none=True)
        
        # Date format conversion
        if params_dict.get('freshness'):
            params_dict['freshness'] = self._convert_date_to_freshness(params_dict['freshness'])
        
        # Remove internal fields
        return {k: v for k, v in params_dict.items() if k not in ['search_lang', 'ui_lang']}

    def image_search(self, params: ImageSearchParams) -> ApiResponse:
        """Perform image search and format response"""
        processed_params = self._process_image_params(params)
        response = self.client.image_search(processed_params)
        
        validated = []
        for item in response.get('results', []):
            # Map Brave's response to our schema
            mapped = {
                'title': item.get('title', ''),
                'url': item.get('properties', {}).get('url', ''),
                'thumbnail': item.get('thumbnail', {}),
                'source': item.get('source', ''),
                'width': self._get_pixel_value(item.get('properties', {}).get('width')),
                'height': self._get_pixel_value(item.get('properties', {}).get('height')),
                'size': item.get('properties', {}).get('size'),
                'aspect_ratio': self._calculate_aspect_ratio(
                    item.get('properties', {}).get('width'),
                    item.get('properties', {}).get('height')
                )
            }
            validated.append(ImageSearchResult(**mapped))
        
        return self.prepare_response(validated, "BraveImageCard")

    def _get_pixel_value(self, value: Optional[str]) -> Optional[int]:
        if value and 'px' in value:
            try:
                return int(value.replace('px', ''))
            except ValueError:
                return None
        return None

    def _calculate_aspect_ratio(self, width: Optional[str], height: Optional[str]) -> Optional[float]:
        try:
            w = self._get_pixel_value(width)
            h = self._get_pixel_value(height)
            if w and h and h != 0:
                return round(w / h, 2)
            return None
        except (TypeError, ValueError):
            return None

    def video_search(self, params: VideoSearchParams) -> ApiResponse:
        """Perform video search and format response"""
        processed_params = self._process_video_params(params)
        response = self.client.video_search(processed_params)
        
        validated = []
        for item in response.get('results', []):
            mapped = {
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'thumbnail': item.get('thumbnail', {}),
                'duration': self._convert_duration(item.get('video', {}).get('duration_sec')),
                'views': self._parse_views(item.get('video', {}).get('views')),
                'publisher': item.get('publisher', ''),
                'published_date': item.get('page_age', ''),
                'description': item.get('description', '')
            }
            validated.append(VideoSearchResult(**mapped))
        
        return self.prepare_response(validated, "BraveVideoCard")

    def _convert_duration(self, seconds: Optional[int]) -> Optional[str]:
        if not seconds:
            return None
        try:
            return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"
        except TypeError:
            return None

    def _parse_views(self, view_data: Optional[Any]) -> Optional[int]:
        """Handle multiple view count formats from API"""
        if not view_data:
            return None
        
        try:
            if isinstance(view_data, int):
                return view_data
            if isinstance(view_data, str):
                return int(view_data.replace(',', '').replace(' views', ''))
            if isinstance(view_data, dict):
                return int(view_data.get('count', 0))
        except (ValueError, TypeError):
            pass
        return None

    def news_search(self, params: NewsSearchParams) -> ApiResponse:
        """Perform news search and format response"""
        processed_params = self._process_news_params(params)
        response = self.client.news_search(processed_params)
        
        validated = []
        for item in response.get('results', []):
            mapped = {
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'description': item.get('description', ''),
                'source': item.get('meta_url', {}).get('netloc', ''),
                'date': item.get('page_age', ''),
                'thumbnail': item.get('thumbnail', {}),
                'authors': item.get('authors', [])
            }
            validated.append(NewsSearchResult(**mapped))
        
        return self.prepare_response(validated, "BraveNewsCard")

    def _process_image_params(self, params: ImageSearchParams) -> Dict[str, Any]:
        """Convert Pydantic model to API parameters"""
        params_dict = params.model_dump(exclude_none=True)
        return params_dict

    def _process_video_params(self, params: VideoSearchParams) -> Dict[str, Any]:
        """Convert Pydantic model to API parameters"""
        params_dict = params.model_dump(exclude_none=True)
        return params_dict

    def _process_news_params(self, params: NewsSearchParams) -> Dict[str, Any]:
        """Convert Pydantic model to API parameters"""
        params_dict = params.model_dump(exclude_none=True)
        if params_dict.get('freshness'):
            params_dict['freshness'] = self._convert_date_to_freshness(params_dict['freshness'])
        return params_dict

    def _convert_date_to_freshness(self, date_str: str) -> str:
        """Convert date formats to Brave's freshness codes while preserving ranges"""
        try:
            # Handle date ranges first (YYYY-MM-DDtoYYYY-MM-DD)
            if 'to' in date_str:
                return date_str
            
            # Handle single date formats
            if len(date_str) == 7:  # YYYY-MM
                return "pm"
            elif len(date_str) == 10:  # YYYY-MM-DD
                return "pd"
        except ValueError:
            pass
        return date_str 