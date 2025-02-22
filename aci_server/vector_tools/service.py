from typing import Dict, Any, Union
from qdrant_client.models import Filter, FieldCondition, MatchValue
from .vector_tools import VectorStoreActions
from .schema import SearchParams, SearchQueryGoogleDrive, SearchQueryNotion, SearchQueryConfluence

class VectorSearchService:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def _build_google_drive_filter(self, query: SearchQueryGoogleDrive) -> Filter:
        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=self.user_id)
            )
        ]

        field_mappings = {
            "doc_id": query.doc_id,
            "title": query.title,
            "modified_time": query.modified_time,
            "web_view_link": query.web_view_link,
            "parent_ids": query.parent_ids
        }

        for field, value in field_mappings.items():
            if value is not None:
                must_conditions.append(
                    FieldCondition(key=field, match=MatchValue(value=value))
                )

        return Filter(must=must_conditions)

    def _build_notion_filter(self, query: SearchQueryNotion) -> Filter:
        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=self.user_id)
            )
        ]

        field_mappings = {
            "doc_id": query.doc_id,
            "title": query.title,
            "database_id": query.database_id,
            "url": query.url,
            "last_edited_time": query.last_edited_time
        }

        for field, value in field_mappings.items():
            if value is not None:
                must_conditions.append(
                    FieldCondition(key=field, match=MatchValue(value=value))
                )

        return Filter(must=must_conditions)

    def _build_confluence_filter(self, query: SearchQueryConfluence) -> Filter:
        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=self.user_id)
            )
        ]

        field_mappings = {
            "doc_id": query.doc_id,
            "title": query.title,
            "space_id": query.space_id,
            "space_name": query.space_name,
            "version": query.version
        }

        for field, value in field_mappings.items():
            if value is not None:
                must_conditions.append(
                    FieldCondition(key=field, match=MatchValue(value=value))
                )

        return Filter(must=must_conditions)

    def search_documents(self, search_params: SearchParams, query_text: str) -> list[Dict[str, Any]]:
        if not search_params.collection:
            raise ValueError("Collection name is required")
        
        if not query_text:
            raise ValueError("Query text is required")
        
        if not self.user_id:
            raise ValueError("User ID is required")

        if search_params.collection == "google-drive":
            search_filter = self._build_google_drive_filter(search_params.query)
        elif search_params.collection == "notion":
            search_filter = self._build_notion_filter(search_params.query)
        elif search_params.collection == "confluence":
            search_filter = self._build_confluence_filter(search_params.query)
        else:
            raise ValueError(f"Unsupported collection: {search_params.collection}")

        vector_store = VectorStoreActions(collection_name=search_params.collection)
        
        search_results = vector_store.run_search_query_with_text(
            text=query_text,
            limit=search_params.limit,
            filters=search_filter
        )

        results = [
            {
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in search_results
        ]

        return results