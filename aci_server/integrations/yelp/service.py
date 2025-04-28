from typing import Dict, Any, List, Optional
import os
from .client import YelpClient
from .schema import (
    SearchBusinessesParams,
    GetBusinessDetailsParams,
    GetBusinessReviewsParams,
    GetBusinessMenusParams,
    Business,
    BusinessSearchResults,
    BusinessReviewResults,
    BusinessMenus,
    BusinessDetailsList,
    ApiResponse,
    BusinessCategory,
    BusinessLocation,
    BusinessCoordinates,
    ReviewUser,
    Review,
    MenuItem,
    MenuSection,
    Menu
)
from ..common.component_handler import load_components, prepare_components_auto

class YelpService:
    def __init__(self, client: YelpClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "yelp"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def search_businesses(self, params: SearchBusinessesParams) -> ApiResponse:
        """
        Search for businesses based on location, search term, and other filters.
        """
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        response = self.client.search_businesses(query_params)
        
        # Process the response - the API returns business_search_result instead of businesses
        business_results = response.get("business_search_result", [])
        total = response.get("total", 0)
        region = response.get("region", {})
        
        # Map the API response format to our schema format
        processed_businesses = []
        for business in business_results:
            # Process categories
            categories = []
            if business.get("categories"):
                for category in business.get("categories", []):
                    categories.append(BusinessCategory(
                        alias=category.get("category_filter"),
                        title=category.get("name")
                    ))
            
            # Process location
            location = BusinessLocation(
                address1=business.get("address1"),
                address2=business.get("address2"),
                address3=business.get("address3"),
                city=business.get("city"),
                state=business.get("state"),
                zip_code=business.get("zip"),
                country=business.get("country"),
                display_address=[business.get("addresses", {}).get("primary_language", {}).get("long_form")] if business.get("addresses") else None
            )
            
            # Process coordinates
            coordinates = BusinessCoordinates(
                latitude=business.get("latitude"),
                longitude=business.get("longitude")
            )
            
            # Map price field
            price_mapping = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
            price = price_mapping.get(business.get("price")) or business.get("localized_price")
            
            # Create a processed business object
            processed_business = Business(
                id=business.get("id"),
                alias=business.get("alias"),
                name=business.get("name"),
                image_url=business.get("photo_url"),
                is_closed=business.get("is_closed", False),
                url=f"https://www.yelp.com/biz/{business.get('alias')}",
                review_count=business.get("review_count"),
                categories=categories,
                rating=business.get("avg_rating"),
                coordinates=coordinates,
                transactions=[],  # Not provided in this API response format
                price=price,
                location=location,
                phone=business.get("phone"),
                display_phone=business.get("localized_phone"),
                distance=None  # Not provided in this API response format
            )
            
            processed_businesses.append(processed_business)
        
        # Create a valid BusinessSearchResults instance
        search_results = BusinessSearchResults(
            total=total,
            businesses=processed_businesses,
            region=region
        )
        
        return self.prepare_response(search_results, "YelpBusinessSearchResults")
    
    def get_business_details(self, params: GetBusinessDetailsParams) -> ApiResponse:
        """
        Get detailed information about a business.
        """
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        response = self.client.get_business_details(query_params)
        
        # The API returns data in "business_details" field which can be a list or dict
        business_details = response.get("business_details", [])
        
        # If no business data found, return empty business
        if not business_details:
            return self.prepare_response(Business(), "YelpBusinessDetails")
        
        # Handle different response formats: business_url returns a dict, business_ids returns a list
        if isinstance(business_details, dict):
            # Single business from URL - process the business data directly
            business_data = business_details
            business = self._process_business_data(business_data)
            return self.prepare_response(business, "YelpBusinessDetails")
        
        # For multiple business IDs, process each one and return as a list
        elif isinstance(business_details, list) and len(business_details) > 0:
            processed_businesses = []
            
            for business_item in business_details:
                # Business data is nested inside the 'business' key in each item
                business_data = business_item.get("business", {})
                
                if not business_data:
                    continue
                
                business = self._process_business_data(business_data)
                processed_businesses.append(business)
            
            # If multiple businesses were requested, return a list 
            if len(processed_businesses) > 1:
                business_list = BusinessDetailsList(businesses=processed_businesses)
                return self.prepare_response(business_list, "YelpBusinessDetailsList")
            # If only one business was requested, return just that business
            elif len(processed_businesses) == 1:
                return self.prepare_response(processed_businesses[0], "YelpBusinessDetails")
            else:
                return self.prepare_response(Business(), "YelpBusinessDetails")
        
        # Fallback case - return empty business
        return self.prepare_response(Business(), "YelpBusinessDetails")
    
    def _process_business_data(self, business_data: dict) -> Business:
        """
        Process raw business data into a Business object.
        """
        # Process categories
        categories = []
        if business_data.get("categories"):
            for category in business_data.get("categories", []):
                categories.append(BusinessCategory(
                    alias=category.get("category_filter"),
                    title=category.get("name")
                ))
        
        # Process location
        location = BusinessLocation(
            address1=business_data.get("address1"),
            address2=business_data.get("address2"),
            address3=business_data.get("address3"),
            city=business_data.get("city"),
            state=business_data.get("state"),
            zip_code=business_data.get("zip"),
            country=business_data.get("country"),
            display_address=[business_data.get("localized_address")] if business_data.get("localized_address") else 
                            [business_data.get("addresses", {}).get("primary_language", {}).get("long_form")] if business_data.get("addresses") else None
        )
        
        # Process coordinates
        coordinates = BusinessCoordinates(
            latitude=business_data.get("latitude"),
            longitude=business_data.get("longitude")
        )
        
        # Process hours - the API returns hours in a special format
        hours = []
        
        # Map price field
        price_mapping = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
        price = price_mapping.get(business_data.get("price")) or business_data.get("localized_price")
        
        # Process photos
        photos = []
        for photo in business_data.get("photos", []):
            if photo.get("url_prefix") and photo.get("url_suffix"):
                photos.append(photo.get("url_prefix") + photo.get("url_suffix"))
        
        # Create a processed business object
        return Business(
            id=business_data.get("id"),
            alias=business_data.get("alias"),
            name=business_data.get("name"),
            image_url=business_data.get("photo_url"),
            is_closed=business_data.get("is_closed", False),
            url=business_data.get("share_url") or f"https://www.yelp.com/biz/{business_data.get('alias')}",
            review_count=business_data.get("review_count"),
            categories=categories,
            rating=business_data.get("avg_rating"),
            coordinates=coordinates,
            transactions=[],  # Not provided in this API response format
            price=price,
            location=location,
            phone=business_data.get("phone"),
            display_phone=business_data.get("localized_phone"),
            photos=photos
        )
    
    def get_business_reviews(self, params: GetBusinessReviewsParams) -> ApiResponse:
        """
        Get reviews for a specific business.
        """
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        response = self.client.get_business_reviews(query_params)
        
        # The API returns reviews in the "reviews" field
        reviews_data = response.get("reviews", [])
        total = response.get("review_count", 0)
        
        # Process the reviews to match our schema
        processed_reviews = []
        for review in reviews_data:
            # Extract user data if available
            user_data = None
            if review.get("author"):
                author = review.get("author", {})
                profile_photo = author.get("profilePhoto", {})
                photo_url = None
                
                # Try to get the photo URL from the nested structure
                if profile_photo and profile_photo.get("photoUrl"):
                    photo_urls = profile_photo.get("photoUrl", {})
                    photo_url = (photo_urls.get("userSrc") or 
                                photo_urls.get("mediaItemSrcUrl"))
                
                user_data = ReviewUser(
                    id=author.get("encid"),
                    profile_url=None,  # Not provided in this API response
                    image_url=photo_url,
                    name=author.get("displayName")
                )
            
            # Get review text from the nested structure
            review_text = ""
            if review.get("text") and isinstance(review.get("text"), dict):
                review_text = review.get("text", {}).get("full", "")
            else:
                review_text = review.get("text", "")
            
            # Create review object
            processed_review = Review(
                id=review.get("encid"),
                url=None,  # Not directly provided in this API response
                text=review_text,
                rating=review.get("rating"),
                time_created=None,  # Not provided in this API response
                user=user_data
            )
            
            processed_reviews.append(processed_review)
        
        # Create a valid BusinessReviewResults instance
        review_results = BusinessReviewResults(
            total=total,
            reviews=processed_reviews,
            possible_languages=response.get("review_counts_by_language", [])
        )
        
        return self.prepare_response(review_results, "YelpBusinessReviews")
    
    def get_business_menus(self, params: GetBusinessMenusParams) -> ApiResponse:
        """
        Get menu information for a specific business by ID.
        """
        response = self.client.get_business_menus(params.business_id)
        
        
        # The API returns menu items as a flat list grouped by categories
        menu_items = response.get("menus", [])
        
        # Group items by category
        categories = {}
        for item in menu_items:
            category_name = item.get("Category", "Menu")
            if category_name not in categories:
                categories[category_name] = []
            
            # Create a proper menu item object
            menu_item = MenuItem(
                name=item.get("Food Name"),
                description=item.get("Details", ""),
                price=item.get("Price", "")
            )
            
            categories[category_name].append(menu_item)
        
        # Create sections from categories
        sections = []
        for category_name, items in categories.items():
            section = MenuSection(
                name=category_name,
                description="",
                items=items
            )
            sections.append(section)
        
        # Create a single menu with all sections
        menu = Menu(
            name="Full Menu",
            sections=sections
        )
        
        # Create a valid BusinessMenus instance
        menus = BusinessMenus(menus=[menu])
        
        return self.prepare_response(menus, "YelpBusinessMenus") 