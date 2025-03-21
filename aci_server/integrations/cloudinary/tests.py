import unittest
import pytest
from unittest.mock import MagicMock, patch
from .client import CloudinaryClient
from .service import CloudinaryService
from .schema import UploadParams, ListAssetsParams, GetAssetDetailsParams


class TestCloudinaryClient:
    """Tests for CloudinaryClient class."""
    
    def setup_method(self):
        self.client = CloudinaryClient("test_cloud", "test_key", "test_secret")
    
    @patch("requests.post")
    def test_upload(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "public_id": "test_image",
            "version": 123456789,
            "format": "jpg",
            "resource_type": "image",
            "created_at": "2023-08-03T14:58:43Z",
            "bytes": 12345,
            "type": "upload",
            "url": "http://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg",
            "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg"
        }
        mock_post.return_value = mock_response
        
        params = {
            "file": "http://example.com/image.jpg",
            "public_id": "test_image",
            "resource_type": "image"
        }
        
        result = self.client.upload(params)
        
        assert result["public_id"] == "test_image"
        assert result["resource_type"] == "image"
        assert "url" in result
        assert "secure_url" in result
    
    @patch("requests.get")
    def test_list_assets(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "resources": [
                {
                    "public_id": "test_image1",
                    "version": 123456789,
                    "format": "jpg",
                    "resource_type": "image",
                    "created_at": "2023-08-03T14:58:43Z",
                    "bytes": 12345,
                    "type": "upload",
                    "url": "http://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image1.jpg",
                    "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image1.jpg"
                }
            ],
            "next_cursor": "next_cursor_value"
        }
        mock_get.return_value = mock_response
        
        params = {
            "max_results": 1,
            "resource_type": "image",
            "type": "upload"
        }
        
        result = self.client.list_assets(params)
        
        assert "resources" in result
        assert len(result["resources"]) == 1
        assert result["resources"][0]["public_id"] == "test_image1"
        assert "next_cursor" in result
    
    @patch("requests.get")
    def test_get_asset_details(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "public_id": "test_image",
            "version": 123456789,
            "format": "jpg",
            "resource_type": "image",
            "created_at": "2023-08-03T14:58:43Z",
            "bytes": 12345,
            "type": "upload",
            "url": "http://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg",
            "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg"
        }
        mock_get.return_value = mock_response
        
        params = {
            "public_id": "test_image",
            "resource_type": "image",
            "type": "upload"
        }
        
        result = self.client.get_asset_details(params)
        
        assert result["public_id"] == "test_image"
        assert result["resource_type"] == "image"
        assert "url" in result
        assert "secure_url" in result


class TestCloudinaryService:
    """Tests for CloudinaryService class."""
    
    def setup_method(self):
        self.mock_client = MagicMock()
        self.service = CloudinaryService(self.mock_client)
        
        # Mock the load_components method
        self.service._load_components = MagicMock(return_value={
            "CloudinaryAssetCard": {
                "name": "CloudinaryAssetCard",
                "displayName": "Cloudinary Asset"
            }
        })
        self.service.components_data = self.service._load_components()
    
    def test_upload(self):
        self.mock_client.upload.return_value = {
            "public_id": "test_image",
            "version": 123456789,
            "format": "jpg",
            "resource_type": "image",
            "created_at": "2023-08-03T14:58:43Z",
            "bytes": 12345,
            "type": "upload",
            "url": "http://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg",
            "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg",
            "tags": []
        }
        
        params = UploadParams(
            file="http://example.com/image.jpg",
            public_id="test_image",
            resource_type="image"
        )
        
        result = self.service.upload(params)
        
        assert result.data.public_id == "test_image"
        assert result.data.resource_type == "image"
        assert result.component is not None
    
    def test_list_assets(self):
        self.mock_client.list_assets.return_value = {
            "resources": [
                {
                    "public_id": "test_image1",
                    "version": 123456789,
                    "format": "jpg",
                    "resource_type": "image",
                    "created_at": "2023-08-03T14:58:43Z",
                    "bytes": 12345,
                    "type": "upload",
                    "url": "http://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image1.jpg",
                    "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image1.jpg"
                }
            ],
            "next_cursor": "next_cursor_value"
        }
        
        params = ListAssetsParams(
            max_results=1,
            resource_type="image"
        )
        
        result = self.service.list_assets(params)
        
        assert len(result.data.resources) == 1
        assert result.data.resources[0].public_id == "test_image1"
        assert result.data.next_cursor == "next_cursor_value"
        assert result.component is not None
    
    def test_get_asset_details(self):
        self.mock_client.get_asset_details.return_value = {
            "public_id": "test_image",
            "version": 123456789,
            "format": "jpg",
            "resource_type": "image",
            "created_at": "2023-08-03T14:58:43Z",
            "bytes": 12345,
            "type": "upload",
            "url": "http://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg",
            "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/test_image.jpg",
            "tags": []
        }
        
        params = GetAssetDetailsParams(
            public_id="test_image",
            resource_type="image"
        )
        
        result = self.service.get_asset_details(params)
        
        assert result.data.public_id == "test_image"
        assert result.data.resource_type == "image"
        assert result.component is not None 