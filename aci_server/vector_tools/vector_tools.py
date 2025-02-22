import os
import uuid
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue
from openai import OpenAI
from dotenv import load_dotenv
from vector_tools.data_sources.base_source import BaseDataSource
from db.supabase import get_supabase

load_dotenv()

class VectorStoreActions:
    def __init__(self, collection_name: str):
        self.client = QdrantClient(os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))
        self.collection_name = collection_name

    def get_collections(self, collection_name: str):
        return self.client.get_collection(collection_name)

    def create_collection(self, collection_name: str):
        try:
            size = 1536
            collection = self.client.create_collection(collection_name, vectors_config=VectorParams(size=size, distance=Distance.COSINE))
            return collection
        except Exception as e:
            raise Exception(f"Error creating collection: {e}")
        
    def generate_vector(self, text: str):
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        vector = response.data[0].embedding
        return vector
        
    def add_vector_to_collection(self, vector: list[float], payload: dict):
        try:
            points = [PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload)]
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=points
            )
            return operation_info
        
        except Exception as e:
            raise Exception(f"Error adding vectors: {e}")
        
    def convert_text_to_vector_and_add_to_collection(self, text: str, payload: dict):
        vector = self.generate_vector(text)
        self.add_vector_to_collection(vector, payload)
        
    def run_vector_search_query_with_vector(self, query_vector: list[float], limit: int = 1000, filters: models.Filter = None):
        try:
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_vector,
                "limit": limit,
            }
            if filters:
                search_params["query_filter"] = filters

            points = self.client.search(**search_params)
            return points
        except Exception as e:
            raise Exception(f"Error running vector search query: {e}")

    def run_search_query_with_text(self, text: str, limit: int = 5, filters: models.Filter = None):
        try:
            query_vector = self.generate_vector(text)
            search_results = self.run_vector_search_query_with_vector(
                query_vector=query_vector,
                limit=limit,
                filters=filters
            )
            return search_results
        except Exception as e:
            raise Exception(f"Error running similarity search query: {e}")

    def process_data_source(self, data_source: BaseDataSource):
        processed_count = 0
        for document in data_source.get_documents():
            try:
                self.convert_text_to_vector_and_add_to_collection(
                    text=document['content'],
                    payload=document['metadata']
                )
                processed_count += 1
            except Exception as e:
                print(f"Error vectorizing document: {e}")
                continue
        return processed_count

    def delete_user_vectors(self, user_id: str) -> int:
        try:
            supabase = get_supabase()
            
            result = supabase.table('users_provider_indexes')\
                .delete()\
                .eq('user_id', user_id)\
                .eq('collection_name', self.collection_name)\
                .execute()

            qdrant_result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
            )
            
            return 1 if qdrant_result.status == 'completed' else 0
        except Exception as e:
            raise Exception(f"Error deleting vectors: {str(e)}")