import requests
from typing import Dict, Any, Optional

class CalClient:
    BASE_URL = "https://api.cal.com/v2"
    API_VERSION = "2024-08-13"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "cal-api-version": self.API_VERSION,
            "Authorization": f"Bearer {api_key}"
        }
    
    def get_bookings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/bookings",
            headers=self.headers,
            params=self._clean_params(params)
        )
        response.raise_for_status()
        return response.json()
    
    def get_booking(self, booking_uid: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/bookings/{booking_uid}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_booking(self, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/bookings",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def reschedule_booking(self, booking_uid: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/bookings/{booking_uid}/reschedule",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def cancel_booking(self, booking_uid: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.BASE_URL}/bookings/{booking_uid}/cancel",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_me(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/me",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_schedules(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/schedules",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_schedule(self, schedule_id: int) -> Dict[str, Any]:
        response = requests.get(
            f"{self.BASE_URL}/schedules/{schedule_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_schedule(self, schedule_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.BASE_URL}/schedules/{schedule_id}",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()
    
    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}
