import requests
from typing import Dict, Any, Optional
from requests.exceptions import HTTPError

class HunterIOClient:
    BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Hunter.io API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        
        # Make the request
        if method.upper() == "GET":
            response = requests.get(url, params=params, headers=self.headers)
        elif method.upper() == "POST":
            response = requests.post(url, params=params, json=data, headers=self.headers)
        elif method.upper() == "PUT":
            response = requests.put(url, params=params, json=data, headers=self.headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, params=params, headers=self.headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    def domain_search(self, domain: Optional[str] = None, company: Optional[str] = None, 
                     limit: Optional[int] = None, offset: Optional[int] = None,
                     type_filter: Optional[str] = None, seniority: Optional[str] = None,
                     department: Optional[str] = None, required_field: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for email addresses from a domain name or company name
        """
        params = {}
        if domain:
            params["domain"] = domain
        if company:
            params["company"] = company
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if type_filter:
            params["type"] = type_filter
        if seniority:
            params["seniority"] = seniority
        if department:
            params["department"] = department
        if required_field:
            params["required_field"] = required_field
            
        return self._make_request("domain-search", params=params)
    
    def email_finder(self, domain: Optional[str] = None, company: Optional[str] = None,
                    first_name: Optional[str] = None, last_name: Optional[str] = None,
                    full_name: Optional[str] = None, max_duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Find the most likely email address from a domain name, first name and last name
        """
        params = {}
        if domain:
            params["domain"] = domain
        if company:
            params["company"] = company
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if full_name:
            params["full_name"] = full_name
        if max_duration:
            params["max_duration"] = max_duration
            
        return self._make_request("email-finder", params=params)
    
    def email_verifier(self, email: str) -> Dict[str, Any]:
        """
        Verify the deliverability of an email address
        """
        params = {"email": email}
        return self._make_request("email-verifier", params=params)
    
    def email_count(self, domain: Optional[str] = None, company: Optional[str] = None, 
                   type_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the number of email addresses we have for a domain or company
        """
        params = {}
        if domain:
            params["domain"] = domain
        if company:
            params["company"] = company
        if type_filter:
            params["type"] = type_filter
            
        return self._make_request("email-count", params=params)
    
    def account_information(self) -> Dict[str, Any]:
        """
        Get information about your Hunter account
        """
        return self._make_request("account")
    
    def email_enrichment(self, email: str, clearbit_format: bool = False) -> Dict[str, Any]:
        """
        Retrieve all the information associated with an email address
        """
        params = {"email": email}
        if clearbit_format:
            params["clearbit_format"] = "1"
            
        return self._make_request("people/find", params=params)
    
    def company_enrichment(self, domain: str, clearbit_format: bool = False) -> Dict[str, Any]:
        """
        Retrieve all the information associated with a domain name
        """
        params = {"domain": domain}
        if clearbit_format:
            params["clearbit_format"] = "1"
            
        return self._make_request("companies/find", params=params)
    
    def combined_enrichment(self, email: str, clearbit_format: bool = False) -> Dict[str, Any]:
        """
        Retrieve all the information associated with an email address and its domain name
        """
        params = {"email": email}
        if clearbit_format:
            params["clearbit_format"] = "1"
            
        return self._make_request("combined/find", params=params) 