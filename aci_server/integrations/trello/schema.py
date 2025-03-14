from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# Base models
class Member(BaseModel):
    id: str
    username: str
    fullName: Optional[str] = None
    avatarUrl: Optional[str] = None

class Board(BaseModel):
    id: str
    name: str
    desc: Optional[str] = None
    closed: bool = False
    url: Optional[str] = None
    shortUrl: Optional[str] = None

class TrelloList(BaseModel):
    id: str
    name: str
    closed: bool = False
    pos: Optional[int] = None
    idBoard: str

class Label(BaseModel):
    id: str
    name: Optional[str] = None
    color: Optional[str] = None

class ChecklistItem(BaseModel):
    id: str
    name: str
    state: str  # "complete" or "incomplete"
    pos: Optional[int] = None

class Checklist(BaseModel):
    id: str
    name: str
    checkItems: Optional[List[ChecklistItem]] = None

class Card(BaseModel):
    id: str
    name: str
    desc: Optional[str] = None
    closed: bool = False
    idBoard: str
    idList: str
    pos: Optional[float] = None
    due: Optional[datetime] = None
    dueComplete: Optional[bool] = False
    labels: Optional[List[Label]] = None
    idMembers: Optional[List[str]] = None
    url: Optional[str] = None
    shortUrl: Optional[str] = None

class CardList(BaseModel):
    items: List[Card]

class Organization(BaseModel):
    id: str
    name: str
    displayName: Optional[str] = None
    desc: Optional[str] = None
    url: Optional[str] = None
    website: Optional[str] = None

# Input schemas
class GetCardsParams(BaseModel):
    board_id: str
    list_id: Optional[str] = Field(
        None, 
        description="List ID. If provided, returns cards from this list only"
    )
    limit: Optional[int] = None

class GetCardParams(BaseModel):
    card_id: str

class CreateCardParams(BaseModel):
    list_id: str
    name: str
    desc: Optional[str] = None
    pos: Optional[str] = "bottom"
    due: Optional[str] = None
    label_ids: Optional[List[str]] = None

class UpdateCardParams(BaseModel):
    card_id: str
    card_update: Dict[str, Any]

class DeleteCardParams(BaseModel):
    card_id: str

class GetBoardsParams(BaseModel):
    member_id: Optional[str] = "me"

class GetBoardParams(BaseModel):
    board_id: str

class GetListsParams(BaseModel):
    board_id: str

class GetListParams(BaseModel):
    list_id: str

class GetCardChecklistsParams(BaseModel):
    card_id: str

class CreateChecklistParams(BaseModel):
    card_id: str
    name: str

class CreateChecklistItemParams(BaseModel):
    checklist_id: str
    name: str
    checked: Optional[bool] = False

class GetOrganizationsParams(BaseModel):
    member_id: Optional[str] = "me"

class GetOrganizationParams(BaseModel):
    org_id: str

class GetOrganizationBoardsParams(BaseModel):
    org_id: str

class GetOrganizationMembersParams(BaseModel):
    org_id: str

# Output schemas
class GetCardsResponse(BaseModel):
    data: CardList
    message: Optional[str] = None

class GetCardResponse(BaseModel):
    data: Card
    message: Optional[str] = None

class CreateCardResponse(BaseModel):
    data: Card
    message: Optional[str] = None

class UpdateCardResponse(BaseModel):
    data: Card
    message: Optional[str] = None

class DeleteCardResponse(BaseModel):
    data: Dict[str, Any]
    message: Optional[str] = None

class GetBoardsResponse(BaseModel):
    data: List[Board]
    message: Optional[str] = None

class GetBoardResponse(BaseModel):
    data: Board
    message: Optional[str] = None

class GetListsResponse(BaseModel):
    data: List[TrelloList]
    message: Optional[str] = None

class GetListResponse(BaseModel):
    data: TrelloList
    message: Optional[str] = None

class GetCardChecklistsResponse(BaseModel):
    data: List[Checklist]
    message: Optional[str] = None

class CreateChecklistResponse(BaseModel):
    data: Checklist
    message: Optional[str] = None

class CreateChecklistItemResponse(BaseModel):
    data: ChecklistItem
    message: Optional[str] = None

class GetOrganizationsResponse(BaseModel):
    data: List[Organization]
    message: Optional[str] = None

class GetOrganizationResponse(BaseModel):
    data: Organization
    message: Optional[str] = None

class GetOrganizationBoardsResponse(BaseModel):
    data: List[Board]
    message: Optional[str] = None

class GetOrganizationMembersResponse(BaseModel):
    data: List[Member]
    message: Optional[str] = None

# API Response
class ApiResponse(BaseModel):
    data: Union[
        Card, CardList, 
        Board, List[Board], 
        TrelloList, List[TrelloList], 
        Checklist, List[Checklist],
        ChecklistItem,
        Organization, List[Organization],
        Member, List[Member],
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
