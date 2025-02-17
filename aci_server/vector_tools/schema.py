from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union
from pydantic import model_validator

class SearchQueryGoogleDrive(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    doc_id: Optional[str] = Field(None, alias='docId')
    title: Optional[str] = None
    modified_time: Optional[str] = Field(None, alias='modifiedTime')
    web_view_link: Optional[str] = Field(None, alias='webViewLink')
    parent_ids: Optional[list[str]] = Field(None, alias='parentIds')

class SearchQueryNotion(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    doc_id: Optional[str] = Field(None, alias='docId')
    title: Optional[str] = None
    database_id: Optional[str] = Field(None, alias='databaseId')
    url: Optional[str] = None
    last_edited_time: Optional[str] = Field(None, alias='lastEditedTime')

class SearchParams(BaseModel):
    query: Union[SearchQueryGoogleDrive, SearchQueryNotion]
    collection: str = Field(..., description="Required collection name")
    limit: Optional[int] = 5

    @model_validator(mode='after')
    def validate_query_type(self):
        if self.collection == "notion":
            if not isinstance(self.query, SearchQueryNotion):
                self.query = SearchQueryNotion(**self.query.model_dump(by_alias=True))
        elif self.collection == "google-drive":
            if not isinstance(self.query, SearchQueryGoogleDrive):
                self.query = SearchQueryGoogleDrive(**self.query.model_dump(by_alias=True))
        return self

class SearchRequest(BaseModel):
    query_text: str
    search_params: SearchParams

    