from typing import Dict, Any, List, Optional
import os
import re
from urllib.parse import urlparse
from .client import DuckDuckGoClient
from .schema import (
    SearchParams,
    ContentParams,
    SearchResult,
    SearchResults,
    Content,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class DuckDuckGoService:
    def __init__(self, client: DuckDuckGoClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "duckduckgo"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def search(self, params: SearchParams) -> ApiResponse:
        raw_data = self.client.search(params.query)
        results = self._process_search_results(raw_data, params.max_results)
        search_results = SearchResults(results=results)
        return self.prepare_response(search_results, "SearchResults")

    def fetch_content(self, params: ContentParams) -> ApiResponse:
        try:
            raw_data = self.client.fetch_content(params.url)
            content = self._process_content(raw_data)
            return self.prepare_response(content, "Content")
        except Exception as e:
            content = Content(
                url=params.url,
                title=None,
                content=None,
                html=None,
                source="duckduckgo"
            )
            return self.prepare_response(content, "Content")

    def _process_search_results(self, data: Dict[str, Any], max_results: int) -> List[SearchResult]:
        results = []
        
        # Process abstract results
        if data.get("AbstractText") and data.get("AbstractURL"):
            results.append(SearchResult(
                title=data.get("Heading", data.get("AbstractSource", "")),
                url=data.get("AbstractURL"),
                description=data.get("AbstractText"),
                source=data.get("AbstractSource"),
                icon=f"https://icons.duckduckgo.com/ip3/{self._get_domain(data.get('AbstractURL'))}.ico"
            ))
        
        # Process related topics
        for topic in data.get("RelatedTopics", []):
            if "Topics" in topic:
                # This is a category
                for subtopic in topic.get("Topics", []):
                    if len(results) >= max_results:
                        break
                    if "Text" in subtopic and "FirstURL" in subtopic:
                        results.append(self._parse_result(subtopic))
            else:
                # This is a direct result
                if len(results) >= max_results:
                    break
                if "Text" in topic and "FirstURL" in topic:
                    results.append(self._parse_result(topic))
        
        # Process results
        for result in data.get("Results", []):
            if len(results) >= max_results:
                break
            if "Text" in result and "FirstURL" in result:
                results.append(self._parse_result(result))
                
        return results[:max_results]
    
    def _parse_result(self, result: Dict[str, Any]) -> SearchResult:
        url = result.get("FirstURL", "")
        text = result.get("Text", "")
        
        # Extract title from Text field - usually the text before the dash or first sentence
        title = ""
        if text:
            # First try to get text before the dash or hyphen
            if " - " in text:
                title = text.split(" - ")[0].strip()
            # If no dash, try to extract the first sentence or use first 50 chars
            else:
                sentences = text.split('. ')
                title = sentences[0].strip()
                if len(title) > 60:
                    title = title[:57] + "..."
        
        return SearchResult(
            title=title,
            url=url,
            description=text,
            source="DuckDuckGo",
            icon=f"https://icons.duckduckgo.com/ip3/{self._get_domain(url)}.ico"
        )
    
    def _process_content(self, data: Dict[str, Any]) -> Content:
        html_content = data.get("html", "")
        return Content(
            url=data.get("url", ""),
            title=self._extract_title(html_content),
            content=self._extract_text_content(html_content),
            html=html_content,
            source="duckduckgo"
        )
    
    def _get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc
        except:
            return ""
    
    def _extract_title(self, html_content: str) -> Optional[str]:
        try:
            title_match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                return title_match.group(1).strip()
        except:
            pass
        return None
    
    def _extract_text_content(self, html_content: str) -> Optional[str]:
        try:
            # Remove script and style elements
            no_script = re.sub(r"<script.*?>.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
            no_style = re.sub(r"<style.*?>.*?</style>", "", no_script, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove HTML tags
            no_tags = re.sub(r"<[^>]*>", " ", no_style)
            
            # Remove extra whitespace
            no_whitespace = re.sub(r"\s+", " ", no_tags).strip()
            
            return no_whitespace
        except:
            return None
