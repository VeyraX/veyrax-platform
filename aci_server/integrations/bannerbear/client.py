import requests
from typing import Any, Dict, Optional

class BannerbearClient:
    BASE_URL = "https://api.bannerbear.com/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        resp = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data if method in ["POST", "PATCH", "DELETE"] else None,
            params=params if method in ["GET"] else None
        )
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    def check_authorization(self) -> Dict[str, Any]:
        return self._request("GET", "/auth")

    def retrieve_account_status(self) -> Dict[str, Any]:
        return self._request("GET", "/account")

    def create_image(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/images", data)

    def retrieve_image(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/images/{uid}")

    def list_all_images(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/images", params=data)

    def create_video(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/videos", data)

    def retrieve_video(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/videos/{uid}")

    def update_video(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PATCH", "/videos", data)

    def list_all_videos(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/videos", params=data)

    def create_collection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/collections", data)

    def retrieve_collection(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/collections/{uid}")

    def list_all_collections(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/collections", params=data)

    def create_animated_gif(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/animated_gifs", data)

    def retrieve_animated_gif(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/animated_gifs/{uid}")

    def list_all_animated_gifs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/animated_gifs", params=data)

    def create_screenshot(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/screenshots", data)

    def retrieve_screenshot(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/screenshots/{uid}")

    def list_all_screenshots(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/screenshots", params=data)

    def create_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/templates", data)

    def duplicate_template(self, source_uid: str) -> Dict[str, Any]:
        return self._request("POST", f"/templates?source={source_uid}")

    def retrieve_template(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/templates/{uid}")

    def update_template(self, uid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PATCH", f"/templates/{uid}", data)

    def list_all_templates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/templates", params=data)

    def import_templates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/templates/import", data)

    def create_template_set(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/template_sets", data)

    def update_template_set(self, uid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PATCH", f"/template_sets/{uid}", data)

    def retrieve_template_set(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/template_sets/{uid}")

    def list_all_template_sets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/template_sets", params=data)

    def create_video_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/video_templates", data)

    def retrieve_video_template(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/video_templates/{uid}")

    def list_all_video_templates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/video_templates", params=data)

    def create_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/sessions", data)

    def retrieve_session(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/sessions/{uid}")

    def list_all_sessions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/sessions", params=data)

    def create_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/webhooks", data)

    def retrieve_webhook(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/webhooks/{uid}")

    def delete_webhook(self, uid: str) -> Dict[str, Any]:
        return self._request("DELETE", f"/webhooks/{uid}")

    def create_movie(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/movies", data)

    def retrieve_movie(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/movies/{uid}")

    def list_all_movies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/movies", params=data)

    def create_diagnosis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/diagnoses", data)

    def retrieve_diagnosis(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/diagnoses/{uid}")

    def create_signed_base(self, uid: str) -> Dict[str, Any]:
        return self._request("POST", f"/templates/{uid}/signed_bases")

    def list_signed_bases(self, uid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", f"/templates/{uid}/signed_bases", params=data)

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/projects", data)

    def retrieve_project(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/projects/{uid}")

    def hydrate_project(self, uid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", f"/projects/{uid}/hydrate", data)

    def list_all_projects(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", "/projects", params=data)

    def list_fonts(self) -> Dict[str, Any]:
        return self._request("GET", "/fonts")

    def list_effects(self) -> Dict[str, Any]:
        return self._request("GET", "/effects")

    def join_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/utilities/pdf/join", data)

    def retrieve_joined_pdf(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/utilities/pdf/join/{uid}")

    def rasterize_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/utilities/pdf/rasterize", data)

    def retrieve_rasterized_pdf(self, uid: str) -> Dict[str, Any]:
        return self._request("GET", f"/utilities/pdf/rasterize/{uid}")