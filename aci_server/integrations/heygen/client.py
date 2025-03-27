import requests
from typing import Dict, Any, Optional

class HeygenClient:
    BASE_URL = "https://api.heygen.com/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "x-api-key": api_key
        }

    def list_avatars(self) -> dict:
        """Get list of available avatars and talking photos"""
        response = requests.get(
            f"{self.BASE_URL}/avatars",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_voices(self) -> Dict[str, Any]:
        """Get list of available voices"""
        response = requests.get(
            f"{self.BASE_URL}/voices",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_avatar_groups(self, include_public: bool = False) -> Dict[str, Any]:
        """Get list of avatar groups"""
        params = {"include_public": include_public}
        response = requests.get(
            f"{self.BASE_URL}/avatar_group.list",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def list_group_avatars(self, group_id: str) -> Dict[str, Any]:
        """Get list of avatars in a specific group"""
        response = requests.get(
            f"{self.BASE_URL}/avatar_group/{group_id}/avatars",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def generate_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new video"""
        response = requests.post(
            f"{self.BASE_URL}/video/generate",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get video generation status"""
        response = requests.get(
            "https://api.heygen.com/v1/video_status.get",
            headers=self.headers,
            params={"video_id": video_id}
        )
        response.raise_for_status()
        return response.json()

    def delete_video(self, video_id: str) -> Dict[str, Any]:
        """Delete a video"""
        response = requests.delete(
            "https://api.heygen.com/v1/video.delete",
            headers=self.headers,
            params={"video_id": video_id}
        )
        response.raise_for_status()
        return response.json()

    def generate_webm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a WebM video with transparent background"""
        response = requests.post(
            "https://api.heygen.com/v1/video.webm",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def list_videos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of videos"""
        response = requests.get(
            "https://api.heygen.com/v1/video.list",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def share_video(self, video_id: str) -> Dict[str, Any]:
        """Generate shareable video URL"""
        response = requests.post(
            "https://api.heygen.com/v1/video/share",
            headers=self.headers,
            json={"video_id": video_id}
        )
        response.raise_for_status()
        return response.json()

    def list_templates(self) -> Dict[str, Any]:
        """Get list of templates"""
        response = requests.get(
            "https://api.heygen.com/v2/templates",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """Get template details"""
        response = requests.get(
            f"https://api.heygen.com/v2/template/{template_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def generate_from_template(self, template_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video from template"""
        response = requests.post(
            f"https://api.heygen.com/v2/template/{template_id}/generate",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages for translation"""
        response = requests.get(
            f"{self.BASE_URL}/video_translate/target_languages",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def translate_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start video translation"""
        response = requests.post(
            f"{self.BASE_URL}/video_translate",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_translation_status(self, video_translate_id: str) -> Dict[str, Any]:
        """Get translation status"""
        response = requests.get(
            f"{self.BASE_URL}/video_translate/{video_translate_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_translation_caption(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get translation caption"""
        response = requests.get(
            f"{self.BASE_URL}/video_translate/caption",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def generate_photo_avatar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate photo avatar photos"""
        response = requests.post(
            f"{self.BASE_URL}/photo_avatar/photo/generate",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    def get_generation_status(self, generation_id: str) -> Dict[str, Any]:
        """Check photo/look generation status"""
        response = requests.get(
            f"{self.BASE_URL}/photo_avatar/generation/{generation_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def add_motion(self, photo_avatar_id: str) -> Dict[str, Any]:
        """Add motion to a photo avatar"""
        response = requests.post(
            f"{self.BASE_URL}/photo_avatar/add_motion",
            headers=self.headers,
            json={"id": photo_avatar_id}
        )
        response.raise_for_status()
        return response.json()

    def add_sound_effect(self, photo_avatar_id: str) -> Dict[str, Any]:
        """Add sound effect to a photo avatar"""
        response = requests.post(
            f"{self.BASE_URL}/photo_avatar/add_sound_effect",
            headers=self.headers,
            json={"id": photo_avatar_id}
        )
        response.raise_for_status()
        return response.json()

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        response = requests.get(
            "https://api.heygen.com/v1/user/me",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_remaining_quota(self) -> Dict[str, Any]:
        """Get remaining quota"""
        response = requests.get(
            f"{self.BASE_URL}/user/remaining_quota",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def upload_asset(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """Upload an asset (image, video, audio)"""
        headers = {
            "Content-Type": content_type,
            "X-Api-Key": self.api_key
        }
        
        with open(file_path, "rb") as file:
            response = requests.post(
                "https://upload.heygen.com/v1/asset",
                headers=headers,
                data=file
            )
        
        response.raise_for_status()
        return response.json()

    def list_folders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List folders"""
        response = requests.get(
            "https://api.heygen.com/v1/folders",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def create_folder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new folder"""
        response = requests.post(
            "https://api.heygen.com/v1/folders/create",
            headers=self.headers,
            json=params
        )
        response.raise_for_status()
        return response.json()

    async def _get(self, endpoint: str) -> dict:
        response = await requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
