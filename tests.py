import pytest
from unittest.mock import MagicMock, patch
from schema import FileFromUrlParams, UploadFromUrlParams

@pytest.mark.asyncio
async def test_upload_from_url(self, service, mock_client):
    # Mock download response
    mock_download_response = MagicMock()
    mock_download_response.content = b"file content"
    mock_download_response.headers = {"Content-Type": "image/png"}
    mock_download_response.raise_for_status = MagicMock()
    
    # Mock prepare upload response
    mock_client.prepare_upload.return_value = [{
        "key": "file_123",
        "fileName": "image.png",
        "fileType": "image/png",
        "fileUrl": "https://example.com/image.png",
        "contentDisposition": "inline",
        "pollingJwt": "test_jwt",
        "pollingUrl": "https://example.com/poll",
        "customId": "image-001",
        "url": "https://example.com/upload",
        "fields": {
            "key": "file_123",
            "Content-Type": "image/png"
        }
    }]
    
    # Mock successful upload to signed URL
    mock_client.upload_to_signed_url = MagicMock()
    
    # Patch the requests.get method for downloading
    with patch("requests.get", return_value=mock_download_response):
        # Set up parameters
        params = UploadFromUrlParams(
            fileUrls=[
                FileFromUrlParams(
                    url="https://example.com/image.png",
                    customId="image-001",
                    slug="imageUploader"
                )
            ],
            metadata={"userId": "user_123"}
        )
        
        # Call the service method
        result = await service.upload_from_url(params)
        
        # Verify the result
        assert len(result.data) == 1
        assert result.data[0].key == "file_123"
        assert result.data[0].fileName == "image.png"
        assert result.data[0].fileType == "image/png"
        assert result.data[0].customId == "image-001"
        
        # Verify prepare_upload was called with correct parameters
        expected_prepare_payload = {
            "files": [{
                "name": "image.png",
                "type": "image/png",
                "size": 12,  # Length of b"file content"
                "customId": "image-001"
            }],
            "slug": "imageUploader",
            "metadata": {"userId": "user_123"}
        }
        mock_client.prepare_upload.assert_called_once_with(expected_prepare_payload)
        
        # Verify upload_to_signed_url was called
        mock_client.upload_to_signed_url.assert_called_once() 