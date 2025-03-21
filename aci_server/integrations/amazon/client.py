import os
from amazon_paapi import AmazonApi, get_asin



class AmazonClient:
    def __init__(self, access_key: str, secret_key: str, associate_tag: str, country: str = "US", throttling: int = 1):
        self.amazon_api = AmazonApi(access_key, secret_key, associate_tag, country, throttling=throttling)

    def search_items(self, keyword: str):
        search_results = self.amazon_api.search_items(keywords=keyword)
        return search_results
        
    def get_items(self, asins):
        return self.amazon_api.get_items(asins)
        
    def get_variations(self, asin):
        return self.amazon_api.get_variations(asin)
        
    def get_browse_nodes(self, browse_node_ids):
        return self.amazon_api.get_browse_nodes(browse_node_ids)
        
    def get_asin_from_url(self, url):
        return get_asin(url)