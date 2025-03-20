import requests
from typing import Dict, Any, Optional, Union, List
from requests.exceptions import HTTPError

class ReplicateClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _prepare_wait_header(self, headers: Dict[str, str], wait: Optional[int] = None) -> Dict[str, str]:
        """
        Utility function to prepare headers with wait parameter if provided.
        Ensures wait time is within allowed limits (1-60 seconds).
        
        Args:
            headers: The current headers dictionary
            wait: Optional wait time in seconds
            
        Returns:
            Updated headers dictionary
        """
        if wait is not None:
            if wait > 60:
                wait = 60  # Maximum wait time is 60 seconds
            elif wait < 1:
                wait = 1   # Minimum wait time is 1 second
            headers["Prefer"] = f"wait={wait}"
        return headers
    
    # ---------- Account ----------
    def get_account(self) -> Dict[str, Any]:
        """
        Get information about the authenticated account
        """
        response = requests.get(
            f"{self.base_url}/account",
            headers=self.headers
        )
        return response.json()

    # ---------- Predictions ----------
    def create_prediction(self, data: Dict[str, Any], wait: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a prediction with the specified model version and parameters
        """
        headers = self.headers.copy()
        headers = self._prepare_wait_header(headers, wait)
            
        response = requests.post(
            f"{self.base_url}/predictions",
            headers=headers,
            json=data
        )
        return response.json()
    
    def list_predictions(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        List all predictions created by the authenticated user
        """
        response = requests.get(
            f"{self.base_url}/predictions",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def get_prediction(self, prediction_id: str) -> Dict[str, Any]:
        """
        Get the current state of a prediction
        """
        response = requests.get(
            f"{self.base_url}/predictions/{prediction_id}",
            headers=self.headers
        )
        return response.json()
    
    def cancel_prediction(self, prediction_id: str) -> Dict[str, Any]:
        """
        Cancel a running prediction
        """
        response = requests.post(
            f"{self.base_url}/predictions/{prediction_id}/cancel",
            headers=self.headers
        )
        return response.json()
    
    # ---------- Deployments ----------
    def create_deployment_prediction(self, deployment_owner: str, deployment_name: str, 
                                    data: Dict[str, Any], wait: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a prediction using a deployment
        """
        headers = self.headers.copy()
        headers = self._prepare_wait_header(headers, wait)
            
        response = requests.post(
            f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}/predictions",
            headers=headers,
            json=data
        )
        return response.json()
    
    def list_deployments(self) -> Dict[str, Any]:
        """
        List all deployments for the authenticated account
        """
        response = requests.get(
            f"{self.base_url}/deployments",
            headers=self.headers
        )

        return response.json()
    
    def get_deployment(self, deployment_owner: str, deployment_name: str) -> Dict[str, Any]:
        """
        Get information about a deployment
        """
        response = requests.get(
            f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}",
            headers=self.headers
        )
        
        return response.json()
    
    def create_deployment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new deployment
        """
        response = requests.post(
            f"{self.base_url}/deployments",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def update_deployment(self, deployment_owner: str, deployment_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing deployment
        """
        response = requests.patch(
            f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def delete_deployment(self, deployment_owner: str, deployment_name: str) -> Dict[str, Any]:
        """
        Delete a deployment
        """
        response = requests.delete(
            f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}",
            headers=self.headers
        )
        
        # Return empty dict if no content
        return {} if not response.content else response.json()
        
    # ---------- Models ----------
    def create_official_model_prediction(self, model_owner: str, model_name: str,
                                        data: Dict[str, Any], wait: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a prediction using an official model
        """
        headers = self.headers.copy()
        headers = self._prepare_wait_header(headers, wait)
            
        response = requests.post(
            f"{self.base_url}/models/{model_owner}/{model_name}/predictions",
            headers=headers,
            json=data
        )
        
        return response.json()
    
    def list_models(self) -> Dict[str, Any]:
        """
        List all public models
        """
        response = requests.get(
            f"{self.base_url}/models",
            headers=self.headers
        )
        
        return response.json()
    
    def get_model(self, model_owner: str, model_name: str) -> Dict[str, Any]:
        """
        Get information about a model
        """
        response = requests.get(
            f"{self.base_url}/models/{model_owner}/{model_name}",
            headers=self.headers
        )
        
        return response.json()
    
    def create_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new model
        """
        response = requests.post(
            f"{self.base_url}/models",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def delete_model(self, model_owner: str, model_name: str) -> Dict[str, Any]:
        """
        Delete a model
        """
        response = requests.delete(
            f"{self.base_url}/models/{model_owner}/{model_name}",
            headers=self.headers
        )
    
        # Return empty dict if no content
        return {} if not response.content else response.json()
    
    def search_models(self, query: str) -> Dict[str, Any]:
        """
        Search for models matching a query
        """
        headers = self.headers.copy()
        headers["Content-Type"] = "text/plain"
        
        response = requests.request(
            "QUERY", 
            f"{self.base_url}/models",
            headers=headers,
            data=query
        )
        
        return response.json()
    
    def list_model_examples(self, model_owner: str, model_name: str) -> Dict[str, Any]:
        """
        List examples for a model
        """
        response = requests.get(
            f"{self.base_url}/models/{model_owner}/{model_name}/examples",
            headers=self.headers
        )
        
        return response.json()
    
    def get_model_readme(self, model_owner: str, model_name: str) -> str:
        """
        Get the README content for a model
        """
        response = requests.get(
            f"{self.base_url}/models/{model_owner}/{model_name}/readme",
            headers=self.headers
        )
        
        return response.text
    
    # ---------- Model versions ----------
    def list_model_versions(self, model_owner: str, model_name: str) -> Dict[str, Any]:
        """
        List versions for a model
        """
        response = requests.get(
            f"{self.base_url}/models/{model_owner}/{model_name}/versions",
            headers=self.headers
        )
        
        return response.json()
    
    def get_model_version(self, model_owner: str, model_name: str, version_id: str) -> Dict[str, Any]:
        """
        Get information about a model version
        """
        response = requests.get(
            f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}",
            headers=self.headers
        )
        
        return response.json()
    
    def delete_model_version(self, model_owner: str, model_name: str, version_id: str) -> Dict[str, Any]:
        """
        Delete a model version
        """
        response = requests.delete(
            f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}",
            headers=self.headers
        )
        
        # Return empty dict if no content
        return {} if not response.content else response.json()
    
    # ---------- Trainings ----------
    def create_training(self, model_owner: str, model_name: str, version_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new training
        """
        response = requests.post(
            f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}/trainings",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def list_trainings(self) -> Dict[str, Any]:
        """
        List all trainings
        """
        response = requests.get(
            f"{self.base_url}/trainings",
            headers=self.headers
        )
        
        return response.json()
    
    def get_training(self, training_id: str) -> Dict[str, Any]:
        """
        Get information about a training
        """
        response = requests.get(
            f"{self.base_url}/trainings/{training_id}",
            headers=self.headers
        )
        
        return response.json()
    
    def cancel_training(self, training_id: str) -> Dict[str, Any]:
        """
        Cancel a training
        """
        response = requests.post(
            f"{self.base_url}/trainings/{training_id}/cancel",
            headers=self.headers
        )
        
        return response.json()
    
    # ---------- Collections ----------
    def list_collections(self) -> Dict[str, Any]:
        """
        List collections of models
        """
        response = requests.get(
            f"{self.base_url}/collections",
            headers=self.headers
        )
        
        return response.json()
    
    def get_collection(self, collection_slug: str) -> Dict[str, Any]:
        """
        Get a collection of models
        """
        response = requests.get(
            f"{self.base_url}/collections/{collection_slug}",
            headers=self.headers
        )
        
        return response.json()
    
    # ---------- Hardware ----------
    def list_hardware(self) -> List[Dict[str, Any]]:
        """
        List available hardware for models
        """
        response = requests.get(
            f"{self.base_url}/hardware",
            headers=self.headers
        )
        
        return response.json()
    
    # ---------- Webhooks ----------
    def get_webhook_secret(self) -> Dict[str, Any]:
        """
        Get the signing secret for the default webhook
        """
        response = requests.get(
            f"{self.base_url}/webhooks/default/secret",
            headers=self.headers
        )
        
        return response.json() 