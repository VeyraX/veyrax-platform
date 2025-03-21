from typing import Dict, Any, List, Optional, Union
import os
from .client import CloudinaryClient, CloudinaryAPIError
from .schema import (
    UploadParams, 
    ExplicitParams,
    ListAssetsParams,
    GetAssetDetailsParams,
    DeleteAssetParams,
    RenameAssetParams,
    UploadResponse,
    ExplicitResponse,
    ListAssetsResponse,
    GetAssetDetailsResponse,
    DeleteAssetResponse,
    RenameAssetResponse,
    ApiResponse,
    BasicResponse,
    ErrorResponse
)
from ..common.component_handler import load_components, prepare_components_auto


class CloudinaryService:
    def __init__(self, client: CloudinaryClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "cloudinary"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def prepare_error_response(self, error: CloudinaryAPIError) -> ApiResponse:
        """Handle CloudinaryAPIError and return a properly formatted error response."""
        error_response = ErrorResponse(
            result="error",
            error_message=error.message,
            error_details=error.errors if hasattr(error, "errors") else None
        )
        return self.prepare_response(error_response, "CloudinaryErrorResult")
    
    def upload(self, params: UploadParams) -> ApiResponse:
        """Upload a file to Cloudinary."""
        try:
            processed_params = self._process_upload_params(params)
            response = self.client.upload(processed_params)
            validated_response = UploadResponse(**response)
            return self.prepare_response(validated_response, "CloudinaryAssetCard")
        except CloudinaryAPIError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = CloudinaryAPIError(str(e))
            return self.prepare_error_response(error)
    
    def explicit(self, params: ExplicitParams) -> ApiResponse:
        """Generate derived transformations for an existing asset."""
        try:
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.explicit(processed_params)
            validated_response = ExplicitResponse(**response)
            return self.prepare_response(validated_response, "CloudinaryAssetCard")
        except CloudinaryAPIError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = CloudinaryAPIError(str(e))
            return self.prepare_error_response(error)
    
    def list_assets(self, params: ListAssetsParams) -> ApiResponse:
        """List assets in the Cloudinary account."""
        try:
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.list_assets(processed_params)
            validated_response = ListAssetsResponse(**response)
            return self.prepare_response(validated_response, "CloudinaryAssetList")
        except CloudinaryAPIError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = CloudinaryAPIError(str(e))
            return self.prepare_error_response(error)
    
    def get_asset_details(self, params: GetAssetDetailsParams) -> ApiResponse:
        """Get details for a specific asset."""
        try:
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.get_asset_details(processed_params)
            validated_response = GetAssetDetailsResponse(**response)
            return self.prepare_response(validated_response, "CloudinaryAssetCard")
        except CloudinaryAPIError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = CloudinaryAPIError(str(e))
            return self.prepare_error_response(error)
    
    def delete_asset(self, params: DeleteAssetParams) -> ApiResponse:
        """Delete an asset."""
        try:
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.delete_asset(processed_params)
            validated_response = DeleteAssetResponse(**response)
            return self.prepare_response(validated_response, "CloudinaryDeleteResult")
        except CloudinaryAPIError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = CloudinaryAPIError(str(e))
            return self.prepare_error_response(error)
    
    def rename_asset(self, params: RenameAssetParams) -> ApiResponse:
        """Rename an asset (change its public ID)."""
        try:
            processed_params = params.model_dump(exclude_none=True)
            response = self.client.rename_asset(processed_params)
            validated_response = RenameAssetResponse(**response)
            return self.prepare_response(validated_response, "CloudinaryRenameResult")
        except CloudinaryAPIError as e:
            return self.prepare_error_response(e)
        except Exception as e:
            error = CloudinaryAPIError(str(e))
            return self.prepare_error_response(error)
    
    def _process_upload_params(self, params: UploadParams) -> Dict[str, Any]:
        """Process upload parameters before sending to the client."""
        return params.model_dump(exclude_none=True) 