import requests
from typing import Dict, Any, Optional
import json

class CalClient:
    BASE_URL = "https://api.cal.com/v2" 
    BOOKINGS_API_VERSION = "2024-08-13"  
    EVENT_TYPES_API_VERSION = "2024-06-14"  
    SCHEDULES_API_VERSION = "2024-06-11"  
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.default_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def _get_headers(self, api_version: str) -> Dict[str, str]:
        headers = self.default_headers.copy()
        headers["cal-api-version"] = api_version
        return headers
    
    def get_bookings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/bookings",
            headers=self._get_headers(self.BOOKINGS_API_VERSION),
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()
    
    def get_booking(self, booking_uid: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/bookings/{booking_uid}",
            headers=self._get_headers(self.BOOKINGS_API_VERSION)
        )
        response.raise_for_status()
        return response.json()
    
    def create_booking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/bookings",
            headers=self._get_headers(self.BOOKINGS_API_VERSION),
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def reschedule_booking(self, booking_uid: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/bookings/{booking_uid}/reschedule",
            headers=self._get_headers(self.BOOKINGS_API_VERSION),
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def cancel_booking(self, booking_uid: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/bookings/{booking_uid}/cancel",
            headers=self._get_headers(self.BOOKINGS_API_VERSION),
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_me(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/me",
            headers=self._get_headers(self.BOOKINGS_API_VERSION)
        )
        response.raise_for_status()
        return response.json()
    
    def get_schedules(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/schedules",
            headers=self._get_headers(self.SCHEDULES_API_VERSION)
        )
        response.raise_for_status()
        return response.json()
    
    def get_schedule(self, schedule_id: int) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/schedules/{schedule_id}",
            headers=self._get_headers(self.SCHEDULES_API_VERSION)
        )
        response.raise_for_status()
        return response.json()
    
    def update_schedule(self, schedule_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/schedules/{schedule_id}",
            headers=self._get_headers(self.SCHEDULES_API_VERSION),
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_event_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query_params = self._clean_params(params)
        
        response = requests.get(
            f"{self.BASE_URL}/event-types",
            headers=self._get_headers(self.EVENT_TYPES_API_VERSION),
            params=query_params
        )
        response.raise_for_status()
        return response.json()
    
    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}
