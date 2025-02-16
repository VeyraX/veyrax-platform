from typing import Dict, Any, Union
from qdrant_client.models import Filter, FieldCondition, MatchValue
from .vector_tools import VectorStoreActions
from .schema import SearchParams, SearchQueryGoogleDrive, SearchQueryNotion

class VectorSearchService:
    def _build_google_drive_filter(self, query: SearchQueryGoogleDrive) -> Filter:
        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=query.user_id)
            )
        ]

        field_mappings = {
            "doc_id": query.doc_id,
            "title": query.title,
            "modified_time": query.modified_time,
            "web_view_link": query.web_view_link,
            "parent_ids": query.parent_ids,
            "part": query.part,
            "total_parts": query.total_parts
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
                match=MatchValue(value=query.user_id)
            )
        ]

        field_mappings = {
            "doc_id": query.doc_id,
            "title": query.title,
            "database_id": query.database_id,
            "url": query.url,
            "last_edited_time": query.last_edited_time,
            "part": query.part,
            "total_parts": query.total_parts
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
            
        query = search_params.query
        if not query.user_id:
            raise ValueError("user_id is required")

        if search_params.collection == "google-drive":
            if not isinstance(query, SearchQueryGoogleDrive):
                raise ValueError("Invalid query type for google-drive collection")
            search_filter = self._build_google_drive_filter(query)
        elif search_params.collection == "notion":
            if not isinstance(query, SearchQueryNotion):
                raise ValueError("Invalid query type for notion collection")
            search_filter = self._build_notion_filter(query)
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