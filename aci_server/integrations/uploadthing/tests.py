import pytest
from unittest.mock import MagicMock, patch
from .client import UploadThingClient
from .service import UploadThingService
from .schema import (
    ListFilesParams, 
    PollUploadParams, 
    GetServerCallbackParams, 
    SetServerCallbackParams,
    PrepareUploadParams,
    FileToUpload,
    UploadFilesParams,
    FileDetails
)


@pytest.fixture
def mock_client():
    client = MagicMock(spec=UploadThingClient)
    return client


@pytest.fixture
def service(mock_client):
    service = UploadThingService(mock_client)
    # Mock the _load_components method to avoid file system operations
    service._load_components = MagicMock(return_value={})
    return service


class TestUploadThingClient:
    def test_list_files(self):
        # Create a mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "hasMore": False,
            "files": [
                {
                    "id": "file_123",
                    "customId": "custom_id_123",
                    "key": "file_123",
                    "name": "test.pdf",
                    "status": "Uploaded",
                    "size": 1024,
                    "uploadedAt": 1717213483400
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        # Patch the requests.post method
        with patch("requests.post", return_value=mock_response):
            client = UploadThingClient("test_api_key")
            payload = {"limit": 10, "offset": 0}
            result = client.list_files(payload)
            
            assert "hasMore" in result
            assert "files" in result
            assert len(result["files"]) == 1
            assert result["files"][0]["name"] == "test.pdf"
    
    def test_poll_upload_still_working(self):
        # Create a mock response for upload in progress
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "still working"
        }
        mock_response.raise_for_status = MagicMock()
        
        # Patch the requests.get method
        with patch("requests.get", return_value=mock_response):
            client = UploadThingClient("test_api_key")
            result = client.poll_upload("file_123")
            
            assert "status" in result
            assert result["status"] == "still working"
    
    def test_poll_upload_done(self):
        # Create a mock response for completed upload
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "done",
            "file": {
                "fileKey": "file_123",
                "fileName": "test.pdf",
                "fileSize": 1024,
                "fileType": "application/pdf",
                "fileUrl": "https://example.com/test.pdf",
                "customId": "custom_123",
                "callbackUrl": "https://example.com/callback",
                "callbackSlug": "test-upload"
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        # Patch the requests.get method
        with patch("requests.get", return_value=mock_response):
            client = UploadThingClient("test_api_key")
            result = client.poll_upload("file_123")
            
            assert "status" in result
            assert result["status"] == "done"
            assert "file" in result
            assert result["file"]["fileName"] == "test.pdf"
    
    def test_get_server_callback(self):
        # Create a mock response for server callback
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok"
        }
        mock_response.raise_for_status = MagicMock()
        
        # Patch the requests.get method
        with patch("requests.get", return_value=mock_response):
            client = UploadThingClient("test_api_key")
            result = client.get_server_callback("test_auth_token")
            
            assert "status" in result
            assert result["status"] == "ok"
    
    def test_set_server_callback(self):
        # Create a mock response for setting server callback
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok"
        }
        mock_response.raise_for_status = MagicMock()
        
        # Patch the requests.post method
        with patch("requests.post", return_value=mock_response):
            client = UploadThingClient("test_api_key")
            payload = {
                "fileKey": "file_123",
                "callbackData": {"processed": True}
            }
            result = client.set_server_callback(payload)
            
            assert "status" in result
            assert result["status"] == "ok"
    
    def test_prepare_upload(self):
        # Create a mock response for prepare upload
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "key": "file_123",
                "fileName": "test.jpg",
                "fileType": "image/jpeg",
                "fileUrl": "https://example.com/test.jpg",
                "contentDisposition": "inline",
                "pollingJwt": "test_jwt",
                "pollingUrl": "https://example.com/poll",
                "customId": "custom_123",
                "url": "https://example.com/upload",
                "fields": {
                    "key": "file_123",
                    "Content-Type": "image/jpeg"
                }
            }
        ]
        mock_response.raise_for_status = MagicMock()
        
        # Patch the requests.post method
        with patch("requests.post", return_value=mock_response):
            client = UploadThingClient("test_api_key")
            payload = {
                "callbackUrl": "https://example.com/callback",
                "callbackSlug": "image-upload",
                "files": [{"name": "test.jpg", "size": 1024, "customId": "custom_123"}],
                "routeConfig": ["image"],
                "metadata": {"userId": "user_123"}
            }
            result = client.prepare_upload(payload)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["key"] == "file_123"
            assert result[0]["fileName"] == "test.jpg"
    
    def test_upload_files(self):
        # Create a mock response for uploading files
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "key": "file_123",
                "fileName": "test.pdf",
                "fileType": "application/pdf",
                "fileUrl": "https://example.com/test.pdf",
                "contentDisposition": "inline",
                "pollingJwt": "test_jwt",
                "pollingUrl": "https://example.com/poll",
                "customId": "custom_123",
                "url": "https://example.com/upload",
                "fields": {
                    "key": "file_123",
                    "Content-Type": "application/pdf"
                }
            }
        ]
        mock_response.raise_for_status = MagicMock()
        
        # Patch the requests.post method
        with patch("requests.post", return_value=mock_response):
            client = UploadThingClient("test_api_key")
            payload = {
                "files": [
                    {
                        "name": "test.pdf",
                        "size": 1024,
                        "type": "application/pdf",
                        "customId": "custom_123"
                    }
                ],
                "acl": "public-read",
                "contentDisposition": "inline",
                "metadata": {"userId": "user_123"}
            }
            result = client.upload_files(payload)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["key"] == "file_123"
            assert result[0]["fileName"] == "test.pdf"
    
    def test_test_connection_success(self):
        # Mock a successful connection test
        client = UploadThingClient("test_api_key")
        client.list_files = MagicMock(return_value={"hasMore": False, "files": []})
        
        assert client.test_connection() is True
    
    def test_test_connection_failure(self):
        # Mock a failed connection test
        client = UploadThingClient("invalid_api_key")
        client.list_files = MagicMock(side_effect=Exception("API Error"))
        
        assert client.test_connection() is False


class TestUploadThingService:
    def test_list_files(self, service, mock_client):
        # Mock client response
        mock_client.list_files.return_value = {
            "hasMore": False,
            "files": [
                {
                    "id": "file_123",
                    "customId": "custom_id_123",
                    "key": "file_123",
                    "name": "test.pdf",
                    "status": "Uploaded",
                    "size": 1024,
                    "uploadedAt": 1717213483400
                }
            ]
        }
        
        # Set up parameters
        params = ListFilesParams(limit=10, offset=0)
        
        # Call the service method
        result = service.list_files(params)
        
        # Verify the result
        assert result.data.hasMore is False
        assert len(result.data.files) == 1
        assert result.data.files[0].name == "test.pdf"
        assert result.data.files[0].key == "file_123"
        
        # Verify client method was called with correct parameters
        expected_payload = {"limit": 10, "offset": 0}
        mock_client.list_files.assert_called_once_with(expected_payload)
    
    def test_poll_upload_still_working(self, service, mock_client):
        # Mock client response for in-progress upload
        mock_client.poll_upload.return_value = {
            "status": "still working"
        }
        
        # Set up parameters
        params = PollUploadParams(fileKey="file_123")
        
        # Call the service method
        result = service.poll_upload(params)
        
        # Verify the result
        assert result.data.status == "still working"
        assert result.data.file is None
        
        # Verify client method was called with correct parameters
        mock_client.poll_upload.assert_called_once_with("file_123")
    
    def test_poll_upload_done(self, service, mock_client):
        # Mock client response for completed upload
        mock_client.poll_upload.return_value = {
            "status": "done",
            "file": {
                "fileKey": "file_123",
                "fileName": "test.pdf",
                "fileSize": 1024,
                "fileType": "application/pdf",
                "fileUrl": "https://example.com/test.pdf",
                "customId": "custom_123",
                "callbackUrl": "https://example.com/callback",
                "callbackSlug": "test-upload"
            },
            "metadata": {
                "userId": "user_123"
            },
            "callbackData": {
                "processed": True
            }
        }
        
        # Set up parameters
        params = PollUploadParams(fileKey="file_123")
        
        # Call the service method
        result = service.poll_upload(params)
        
        # Verify the result
        assert result.data.status == "done"
        assert result.data.file is not None
        assert result.data.file.fileName == "test.pdf"
        assert result.data.file.fileKey == "file_123"
        assert result.data.metadata == {"userId": "user_123"}
        assert result.data.callbackData == {"processed": True}
        
        # Verify client method was called with correct parameters
        mock_client.poll_upload.assert_called_once_with("file_123")
    
    def test_get_server_callback(self, service, mock_client):
        # Mock client response
        mock_client.get_server_callback.return_value = {
            "status": "ok"
        }
        
        # Set up parameters
        params = GetServerCallbackParams(authorization="test_auth_token")
        
        # Call the service method
        result = service.get_server_callback(params)
        
        # Verify the result
        assert result.data.status == "ok"
        
        # Verify client method was called with correct parameters
        mock_client.get_server_callback.assert_called_once_with("test_auth_token")
    
    def test_set_server_callback(self, service, mock_client):
        # Mock client response
        mock_client.set_server_callback.return_value = {
            "status": "ok"
        }
        
        # Set up parameters
        callback_data = {"processed": True, "thumbnailUrl": "https://example.com/thumb.jpg"}
        params = SetServerCallbackParams(fileKey="file_123", callbackData=callback_data)
        
        # Call the service method
        result = service.set_server_callback(params)
        
        # Verify the result
        assert result.data.status == "ok"
        
        # Verify client method was called with correct parameters
        expected_payload = {
            "fileKey": "file_123",
            "callbackData": callback_data
        }
        mock_client.set_server_callback.assert_called_once_with(expected_payload)
    
    def test_prepare_upload(self, service, mock_client):
        # Mock client response
        mock_client.prepare_upload.return_value = [
            {
                "key": "file_123",
                "fileName": "test.jpg",
                "fileType": "image/jpeg",
                "fileUrl": "https://example.com/test.jpg",
                "contentDisposition": "inline",
                "pollingJwt": "test_jwt",
                "pollingUrl": "https://example.com/poll",
                "customId": "custom_123",
                "url": "https://example.com/upload",
                "fields": {
                    "key": "file_123",
                    "Content-Type": "image/jpeg"
                }
            }
        ]
        
        # Set up parameters
        files = [FileToUpload(name="test.jpg", size=1024, customId="custom_123")]
        params = PrepareUploadParams(
            callbackUrl="https://example.com/callback",
            callbackSlug="image-upload",
            files=files,
            routeConfig=["image"],
            metadata={"userId": "user_123"}
        )
        
        # Call the service method
        result = service.prepare_upload(params)
        
        # Verify the result
        assert len(result.data) == 1
        assert result.data[0].key == "file_123"
        assert result.data[0].fileName == "test.jpg"
        assert result.data[0].customId == "custom_123"
        
        # Verify client method was called with correct parameters
        expected_payload = {
            "callbackUrl": "https://example.com/callback",
            "callbackSlug": "image-upload",
            "files": [{"name": "test.jpg", "size": 1024, "customId": "custom_123"}],
            "routeConfig": ["image"],
            "metadata": {"userId": "user_123"}
        }
        mock_client.prepare_upload.assert_called_once_with(expected_payload)
        
    def test_upload_files_single_part(self, service, mock_client):
        # Mock client response for single-part upload
        mock_client.upload_files.return_value = [
            {
                "key": "file_123",
                "fileName": "test.pdf",
                "fileType": "application/pdf",
                "fileUrl": "https://example.com/test.pdf",
                "contentDisposition": "inline",
                "pollingJwt": "test_jwt",
                "pollingUrl": "https://example.com/poll",
                "customId": "custom_123",
                "url": "https://example.com/upload",
                "fields": {
                    "key": "file_123",
                    "Content-Type": "application/pdf"
                }
            }
        ]
        
        # Set up parameters
        files = [FileDetails(
            name="test.pdf",
            size=1024,
            type="application/pdf",
            customId="custom_123"
        )]
        params = UploadFilesParams(
            files=files,
            acl="public-read",
            contentDisposition="inline",
            metadata={"userId": "user_123"}
        )
        
        # Call the service method
        result = service.upload_files(params)
        
        # Verify the result
        assert len(result.data) == 1
        assert result.data[0].key == "file_123"
        assert result.data[0].fileName == "test.pdf"
        assert result.data[0].fileType == "application/pdf"
        assert result.data[0].customId == "custom_123"
        assert result.component.name == "UploadThingPreparedUpload"
        assert len(result.component.uploads) == 1
        assert result.component.uploads[0].fileName == "test.pdf"
        assert result.component.uploads[0].uploadType == "Single Part"
        
        # Verify client method was called with correct parameters
        expected_payload = {
            "files": [{
                "name": "test.pdf",
                "size": 1024,
                "type": "application/pdf",
                "customId": "custom_123"
            }],
            "acl": "public-read",
            "contentDisposition": "inline",
            "metadata": {"userId": "user_123"}
        }
        mock_client.upload_files.assert_called_once_with(expected_payload)
        
    def test_upload_files_multi_part(self, service, mock_client):
        # Mock client response for multi-part upload
        mock_client.upload_files.return_value = [
            {
                "key": "file_123",
                "fileName": "small.pdf",
                "fileType": "application/pdf",
                "fileUrl": "https://example.com/small.pdf",
                "contentDisposition": "inline",
                "pollingJwt": "test_jwt_1",
                "pollingUrl": "https://example.com/poll/file_123",
                "customId": "custom_123",
                "url": "https://example.com/upload/file_123",
                "fields": {
                    "key": "file_123",
                    "Content-Type": "application/pdf"
                }
            },
            {
                "key": "file_456",
                "fileName": "large.mp4",
                "fileType": "video/mp4",
                "fileUrl": "https://example.com/large.mp4",
                "contentDisposition": "attachment",
                "pollingJwt": "test_jwt_2",
                "pollingUrl": "https://example.com/poll/file_456",
                "customId": "custom_456",
                "urls": [
                    "https://example.com/upload/file_456-part1",
                    "https://example.com/upload/file_456-part2",
                    "https://example.com/upload/file_456-part3"
                ],
                "uploadId": "multipart_123",
                "chunkSize": 20971520,
                "chunkCount": 3
            }
        ]
        
        # Set up parameters
        files = [
            FileDetails(
                name="small.pdf",
                size=1024,
                type="application/pdf",
                customId="custom_123"
            ),
            FileDetails(
                name="large.mp4",
                size=60000000,
                type="video/mp4",
                customId="custom_456"
            )
        ]
        params = UploadFilesParams(
            files=files,
            acl="private",
            contentDisposition="attachment",
            metadata={"projectId": "project_123"}
        )
        
        # Call the service method
        result = service.upload_files(params)
        
        # Verify the result
        assert len(result.data) == 2
        assert result.data[0].key == "file_123"
        assert result.data[0].fileName == "small.pdf"
        assert result.data[1].key == "file_456"
        assert result.data[1].fileName == "large.mp4"
        assert "urls" in result.data[1].dict()
        assert result.component.name == "UploadThingPreparedUpload"
        assert len(result.component.uploads) == 2
        assert result.component.uploads[0].fileName == "small.pdf"
        assert result.component.uploads[0].uploadType == "Single Part"
        assert result.component.uploads[1].fileName == "large.mp4"
        assert result.component.uploads[1].uploadType == "Multi Part"
        
        # Verify client method was called with correct parameters
        expected_payload = {
            "files": [
                {
                    "name": "small.pdf",
                    "size": 1024,
                    "type": "application/pdf",
                    "customId": "custom_123"
                },
                {
                    "name": "large.mp4",
                    "size": 60000000,
                    "type": "video/mp4",
                    "customId": "custom_456"
                }
            ],
            "acl": "private",
            "contentDisposition": "attachment",
            "metadata": {"projectId": "project_123"}
        }
        mock_client.upload_files.assert_called_once_with(expected_payload) 