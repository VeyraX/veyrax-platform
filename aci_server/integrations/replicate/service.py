from typing import Dict, Any, Union, List, Optional
from .client import ReplicateClient
from .schema import (
    PredictionRequest, 
    DeploymentPredictionRequest, 
    OfficialModelPredictionRequest,
    PredictionResponse, 
    PredictionList,
    TrainingRequest,
    TrainingResponse,
    TrainingList,
    Model,
    ModelList,
    ModelVersion,
    ModelVersionList,
    CollectionList,
    CollectionWithModels,
    DeploymentResponse,
    DeploymentList,
    DeploymentCreationRequest,
    DeploymentUpdateRequest,
    Hardware,
    AccountInfo,
    WebhookSecret,
    ApiResponse,
    ModelCreationRequest
)
import os
from ..common.component_handler import load_components, prepare_components_auto
import time
import datetime

class ReplicateService:
    def __init__(self, client: ReplicateClient):
        self.client = client
        self.components_data = self._load_components()
        
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "replicate"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    # ---------- Account ----------
    def get_account_info(self) -> ApiResponse:
        """
        Get information about the authenticated account
        """
        response = self.client.get_account()
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        account_info = AccountInfo(**response)
        return self.prepare_response(account_info)
        
    # ---------- Predictions ----------
    def create_prediction(self, request: PredictionRequest) -> ApiResponse:
        """
        Create a prediction with a specific model version
        """
        # Transform the request to the format expected by the client
        data = request.model_dump(exclude_none=True)

        wait = request.wait
        
        response = self.client.create_prediction(data, wait=wait)
        prediction_response = PredictionResponse(**response)
        return self.prepare_response(prediction_response, "ReplicatePredictionView")
    
    def list_predictions(self, created_after: Optional[str] = None, created_before: Optional[str] = None) -> ApiResponse:
        """
        List all predictions created by the authenticated user
        """
        # Prepare query parameters
        params = {}
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
            
        response = self.client.list_predictions(params)
        prediction_list = PredictionList(**response)
        return self.prepare_response(prediction_list, "ReplicatePredictionListView")
    
    def get_prediction(self, prediction_id: str) -> ApiResponse:
        """
        Get the current state of a prediction
        """
        response = self.client.get_prediction(prediction_id)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
        
        artefact_urls = []
        
        # Extract URLs from output
        if "output" in response:
            output = response["output"]
            
            # Handle list output
            if isinstance(output, list):
                for item in output:
                    if isinstance(item, str) and (item.startswith("http://") or item.startswith("https://")):
                        # Check for image/video extensions
                        if any(item.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.webm']):
                            artefact_urls.append(item)
                        
            # Handle dict output
            elif isinstance(output, dict):
                for value in output.values():
                    if isinstance(value, str) and (value.startswith("http://") or value.startswith("https://")):
                        # Check for image/video extensions
                        if any(value.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.webm']):
                            artefact_urls.append(value)
        
        response["artefacts_urls"] = artefact_urls
        
        prediction_response = PredictionResponse(**response)
        return self.prepare_response(prediction_response, "ReplicatePredictionView")
    
    def cancel_prediction(self, prediction_id: str) -> ApiResponse:
        """
        Cancel a running prediction
        """
        response = self.client.cancel_prediction(prediction_id)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        prediction_response = PredictionResponse(**response)
        return self.prepare_response(prediction_response, "ReplicatePredictionView")
    
    # ---------- Deployments ----------
    def create_deployment_prediction(
        self, 
        deployment_owner: str,
        deployment_name: str,
        request: DeploymentPredictionRequest,
        wait: Optional[int] = None
    ) -> ApiResponse:
        """
        Create a prediction using a deployment
        """
        # Transform the request to the format expected by the client
        data = request.model_dump(exclude_none=True)
        
        response = self.client.create_deployment_prediction(
            deployment_owner=deployment_owner,
            deployment_name=deployment_name,
            data=data,
            wait=wait
        )
        
        prediction_response = PredictionResponse(**response)
        return self.prepare_response(prediction_response, "ReplicatePredictionView")
    
    def list_deployments(self) -> ApiResponse:
        """
        List all deployments for the authenticated account
        """
        response = self.client.list_deployments()
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        deployment_list = DeploymentList(**response)
        return self.prepare_response(deployment_list, "ReplicateDeploymentListView")
    
    def get_deployment(self, deployment_owner: str, deployment_name: str) -> ApiResponse:
        """
        Get information about a deployment
        """
        response = self.client.get_deployment(deployment_owner, deployment_name)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        deployment_response = DeploymentResponse(**response)
        return self.prepare_response(deployment_response, "ReplicateDeploymentView")
    
    def create_deployment(self, request: DeploymentCreationRequest) -> ApiResponse:
        """
        Create a new deployment
        """
        # Transform the request to the format expected by the client
        data = request.model_dump(exclude_none=True)
        
        response = self.client.create_deployment(data)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        deployment_response = DeploymentResponse(**response)
        return self.prepare_response(deployment_response, "ReplicateDeploymentView")
    
    def update_deployment(self, deployment_owner: str, deployment_name: str, 
                         request: DeploymentUpdateRequest) -> ApiResponse:
        """
        Update an existing deployment
        """
        # Transform the request to the format expected by the client
        data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        response = self.client.update_deployment(
            deployment_owner=deployment_owner,
            deployment_name=deployment_name,
            data=data
        )
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        deployment_response = DeploymentResponse(**response)
        return self.prepare_response(deployment_response, "ReplicateDeploymentView")
    
    def delete_deployment(self, deployment_owner: str, deployment_name: str) -> ApiResponse:
        """
        Delete a deployment
        """
        response = self.client.delete_deployment(deployment_owner, deployment_name)
        # Return empty response with success message
        return self.prepare_response({"success": True, "message": "Deployment deleted"})
    
    # ---------- Models ----------
    def create_official_model_prediction(
        self,
        model_owner: str,
        model_name: str,
        request: OfficialModelPredictionRequest
    ) -> ApiResponse:
        """
        Create a prediction using an official model
        """
        # Transform the request to the format expected by the client
        data = request.model_dump(exclude_none=True)
        
        # Special case for Minimax video model - use only the input field
        is_minimax_video = model_owner == "minimax" and model_name == "video-01"
        if is_minimax_video:
            # For Minimax, only send the input field
            data = {"input": data.get("input", {})}
            print(f"[SERVICE] Sending simplified data to Minimax: {data}")
        else:
            # For other models, remove fields not expected by the API
            if "model_owner" in data:
                data.pop("model_owner")
            if "model_name" in data:
                data.pop("model_name")
            if "create_placeholder_response" in data:
                create_placeholder = data.pop("create_placeholder_response")
            else:
                create_placeholder = False
        
        wait = request.wait
        
        response = self.client.create_official_model_prediction(
            model_owner=model_owner,
            model_name=model_name,
            data=data,
            wait=wait
        )
        
        print(f'[create_official_model_prediction] response for {model_owner}/{model_name}: {response}')
        
        # Check if response is an error response
        if "error" in response and "detail" in response:
            # Handle API error response
            error_message = response.get("detail", "Unknown error from Replicate API")
            raise ValueError(f"Replicate API error: {error_message}")
            
        if not response:
            raise ValueError("Empty response received from Replicate API")
        
        # Ensure required fields exist
        required_fields = ["id", "model", "created_at", "input", "urls"]
        missing_fields = [field for field in required_fields if field not in response]
        
        # Special handling for Minimax video model which may return partial data
        if is_minimax_video and missing_fields:
            print(f"Creating placeholder response for Minimax video model. Missing fields: {missing_fields}")
            # Create placeholder data for missing fields
            if "id" not in response:
                response["id"] = f"placeholder-{model_owner}-{model_name}-{int(time.time())}"
            if "model" not in response:
                response["model"] = f"{model_owner}/{model_name}"
            if "created_at" not in response:
                response["created_at"] = datetime.datetime.now().isoformat()
            if "input" not in response:
                response["input"] = data.get("input", {})
            if "urls" not in response:
                response["urls"] = {
                    "get": f"https://api.replicate.com/v1/predictions/{response.get('id', 'placeholder')}",
                    "cancel": f"https://api.replicate.com/v1/predictions/{response.get('id', 'placeholder')}/cancel"
                }
            if "status" not in response:
                response["status"] = "processing"
            
            missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in API response: {', '.join(missing_fields)}")
        
        # Create URLs object if not present but individual URL fields exist
        if "urls" not in response and ("get" in response or "cancel" in response):
            response["urls"] = {
                "get": response.get("get", ""),
                "cancel": response.get("cancel", "")
            }
        
        # Ensure status is a valid string
        if "status" not in response or not isinstance(response["status"], str):
            response["status"] = "processing"  # Default status
            
        try:
            prediction_response = PredictionResponse(**response)
            return self.prepare_response(prediction_response, "ReplicatePredictionView")
        except Exception as e:
            print(f"Failed to parse response: {e}")
            print(f"Response data: {response}")
            raise ValueError(f"Failed to parse Replicate API response: {str(e)}")
    
    def list_models(self) -> ApiResponse:
        """
        List all public models
        """
        response = self.client.list_models()
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        model_list = ModelList(**response)
        return self.prepare_response(model_list, "ReplicateModelListView")
    
    def get_model(self, model_owner: str, model_name: str) -> ApiResponse:
        """
        Get information about a model
        """
        response = self.client.get_model(model_owner, model_name)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        model = Model(**response)
        return self.prepare_response(model, "ReplicateModelView")
    
    def create_model(self, request: ModelCreationRequest) -> ApiResponse:
        """
        Create a new model
        """
        # Transform the request to the format expected by the client
        data = request.model_dump(exclude_none=True)
        
        response = self.client.create_model(data)
        model = Model(**response)
        return self.prepare_response(model, "ReplicateModelView")
    
    def delete_model(self, model_owner: str, model_name: str) -> ApiResponse:
        """
        Delete a model
        """
        response = self.client.delete_model(model_owner, model_name)
        # Return empty response with succeeess message
        return self.prepare_response({"success": True, "message": "Model deleted"})
    
    def search_models(self, query: str) -> ApiResponse:
        """
        Search for models matching a query
        """
        response = self.client.search_models(query)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        model_list = ModelList(**response)
        return self.prepare_response(model_list, "ReplicateModelListView")
    
    def list_model_examples(self, model_owner: str, model_name: str) -> ApiResponse:
        """
        List examples for a model
        """
        response = self.client.list_model_examples(model_owner, model_name)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        prediction_list = PredictionList(**response)
        return self.prepare_response(prediction_list, "ReplicatePredictionListView")
    
    def get_model_readme(self, model_owner: str, model_name: str) -> ApiResponse:
        """
        Get the README content for a model
        """
        response = self.client.get_model_readme(model_owner, model_name)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        return self.prepare_response(response, "ReplicateReadmeView")
    
    # ---------- Model versions ----------
    def list_model_versions(self, model_owner: str, model_name: str) -> ApiResponse:
        """
        List versions for a model
        """
        response = self.client.list_model_versions(model_owner, model_name)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        model_version_list = ModelVersionList(**response)
        return self.prepare_response(model_version_list, "ReplicateModelVersionListView")
    
    def get_model_version(self, model_owner: str, model_name: str, version_id: str) -> ApiResponse:
        """
        Get information about a model version
        """
        response = self.client.get_model_version(model_owner, model_name, version_id)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        model_version = ModelVersion(**response)
        return self.prepare_response(model_version, "ReplicateModelVersionView")
    
    def delete_model_version(self, model_owner: str, model_name: str, version_id: str) -> ApiResponse:
        """
        Delete a model version
        """
        response = self.client.delete_model_version(model_owner, model_name, version_id)
        # Return empty response with success message
        return self.prepare_response({"success": True, "message": "Model version deleted"})
    
    # ---------- Trainings ----------
    def create_training(self, model_owner: str, model_name: str, version_id: str,
                       request: TrainingRequest) -> ApiResponse:
        """
        Create a new training
        """
        # Transform the request to the format expected by the client
        data = request.model_dump(exclude_none=True)
        
        response = self.client.create_training(
            model_owner=model_owner,
            model_name=model_name,
            version_id=version_id,
            data=data
        )
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        training_response = TrainingResponse(**response)
        return self.prepare_response(training_response, "ReplicateTrainingView")
    
    def list_trainings(self) -> ApiResponse:
        """
        List all trainings
        """
        response = self.client.list_trainings()
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        training_list = TrainingList(**response)
        return self.prepare_response(training_list, "ReplicateTrainingListView")
    
    def get_training(self, training_id: str) -> ApiResponse:
        """
        Get information about a training
        """
        response = self.client.get_training(training_id)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        training_response = TrainingResponse(**response)
        return self.prepare_response(training_response, "ReplicateTrainingView")
    
    def cancel_training(self, training_id: str) -> ApiResponse:
        """
        Cancel a training
        """
        response = self.client.cancel_training(training_id)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        training_response = TrainingResponse(**response)
        return self.prepare_response(training_response, "ReplicateTrainingView")
    
    # ---------- Collections ----------
    def list_collections(self) -> ApiResponse:
        """
        List collections of models
        """
        response = self.client.list_collections()
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        collection_list = CollectionList(**response)
        return self.prepare_response(collection_list, "ReplicateCollectionListView")
    
    def get_collection(self, collection_slug: str) -> ApiResponse:
        """
        Get a collection of models
        """
        response = self.client.get_collection(collection_slug)
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        collection_with_models = CollectionWithModels(**response)
        return self.prepare_response(collection_with_models, "ReplicateCollectionView")
    
    # ---------- Hardware ----------
    def list_hardware(self) -> ApiResponse:
        """
        List available hardware for models
        """
        response = self.client.list_hardware()
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        hardware_list = [Hardware(**hw) for hw in response]
        return self.prepare_response(hardware_list, "ReplicateHardwareListView")
    
    # ---------- Webhooks ----------
    def get_webhook_secret(self) -> ApiResponse:
        """
        Get the signing secret for the default webhook
        """
        response = self.client.get_webhook_secret()
        
        if not response:
            raise ValueError("Empty response received from Replicate API")
            
        webhook_secret = WebhookSecret(**response)
        return self.prepare_response(webhook_secret, "ReplicateWebhookSecretView") 