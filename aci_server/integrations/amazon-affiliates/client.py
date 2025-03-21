from amazon_paapi import AmazonApi
import os




class AmazonClient:
    def __init__(self, access_key: str, secret_key: str, associate_tag: str, country: str = "US"):
        # ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
        # SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
        # ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
        # COUNTRY = 'US'  # For Amazon.com; use 'de' for Germany, 'fr' for France, etc.
        amazon_api = AmazonApi(access_key, secret_key, associate_tag, country)
        self.amazon_api = amazon_api

    def search_items(self, keyword: str):
        search_results = self.amazon_api.search_items(keywords=keyword)
        return search_results