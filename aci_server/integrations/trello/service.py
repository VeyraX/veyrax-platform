from typing import Optional, List, Dict, Any, Union
from .client import TrelloClient
from .schema import (
    Card, CardList, Board, TrelloList, ApiResponse,
    Member, Checklist, ChecklistItem, Label, Organization
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class TrelloService:
    def __init__(self, client: TrelloClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "trello"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _convert_to_card(self, card_data: Dict[str, Any]) -> Card:
        labels = []
        if card_data.get('labels'):
            for label in card_data['labels']:
                labels.append(Label(
                    id=label.get('id', ''),
                    name=label.get('name'),
                    color=label.get('color')
                ))
        
        return Card(
            id=card_data.get('id', ''),
            name=card_data.get('name', ''),
            desc=card_data.get('desc'),
            closed=card_data.get('closed', False),
            idBoard=card_data.get('idBoard', ''),
            idList=card_data.get('idList', ''),
            pos=card_data.get('pos'),
            due=card_data.get('due'),
            dueComplete=card_data.get('dueComplete', False),
            labels=labels or None,
            idMembers=card_data.get('idMembers'),
            url=card_data.get('url'),
            shortUrl=card_data.get('shortUrl')
        )

    def get_cards(self, board_id: str, list_id: Optional[str] = None, 
                 limit: Optional[int] = None) -> ApiResponse:
        try:
            response = self.client.get_cards(
                board_id=board_id,
                list_id=list_id,
                limit=limit
            )
            
            cards = [self._convert_to_card(card) for card in response]
            
            card_list = CardList(
                items=cards
            )
            
            return self.prepare_response(card_list, "TrelloCardList")
        except Exception as e:
            raise ValueError(f"Error getting cards: {str(e)}")

    def get_card(self, card_id: str) -> ApiResponse:
        try:
            response = self.client.get_card(card_id)
            card = self._convert_to_card(response)
            return self.prepare_response(card, "TrelloCardDetail")
        except Exception as e:
            raise ValueError(f"Error getting card: {str(e)}")

    def create_card(self, list_id: str, name: str, desc: Optional[str] = None, 
                   pos: Optional[str] = "bottom", due: Optional[str] = None,
                   label_ids: Optional[List[str]] = None) -> ApiResponse:
        try:
            response = self.client.create_card(
                list_id=list_id,
                name=name,
                desc=desc,
                pos=pos,
                due=due,
                label_ids=label_ids
            )
            card = self._convert_to_card(response)
            return self.prepare_response(card, "TrelloCardDetail")
        except Exception as e:
            raise ValueError(f"Error creating card: {str(e)}")

    def update_card(self, card_id: str, card_update: Dict[str, Any]) -> ApiResponse:
        try:
            response = self.client.update_card(card_id, card_update)
            card = self._convert_to_card(response)
            return self.prepare_response(card, "TrelloCardDetail")
        except Exception as e:
            raise ValueError(f"Error updating card: {str(e)}")

    def delete_card(self, card_id: str) -> ApiResponse:
        try:
            response = self.client.delete_card(card_id)
            return self.prepare_response(response, None)
        except Exception as e:
            raise ValueError(f"Error deleting card: {str(e)}")

    def _convert_to_board(self, board_data: Dict[str, Any]) -> Board:
        return Board(
            id=board_data.get('id', ''),
            name=board_data.get('name', ''),
            desc=board_data.get('desc'),
            closed=board_data.get('closed', False),
            url=board_data.get('url'),
            shortUrl=board_data.get('shortUrl')
        )

    def get_boards(self, member_id: str = "me") -> ApiResponse:
        try:
            response = self.client.get_boards(member_id)
            boards = [self._convert_to_board(board) for board in response]
            return self.prepare_response(boards, "TrelloBoardList")
        except Exception as e:
            raise ValueError(f"Error getting boards: {str(e)}")

    def get_board(self, board_id: str) -> ApiResponse:
        try:
            response = self.client.get_board(board_id)
            board = self._convert_to_board(response)
            return self.prepare_response(board, "TrelloBoardDetail")
        except Exception as e:
            raise ValueError(f"Error getting board: {str(e)}")

    def _convert_to_list(self, list_data: Dict[str, Any]) -> TrelloList:
        return TrelloList(
            id=list_data.get('id', ''),
            name=list_data.get('name', ''),
            closed=list_data.get('closed', False),
            pos=list_data.get('pos'),
            idBoard=list_data.get('idBoard', '')
        )

    def get_lists(self, board_id: str) -> ApiResponse:
        try:
            response = self.client.get_lists(board_id)
            lists = [self._convert_to_list(list_data) for list_data in response]
            return self.prepare_response(lists, "TrelloListList")
        except Exception as e:
            raise ValueError(f"Error getting lists: {str(e)}")

    def get_list(self, list_id: str) -> ApiResponse:
        try:
            response = self.client.get_list(list_id)
            trello_list = self._convert_to_list(response)
            return self.prepare_response(trello_list, "TrelloListDetail")
        except Exception as e:
            raise ValueError(f"Error getting list: {str(e)}")

    def _convert_to_checklist_item(self, item_data: Dict[str, Any]) -> ChecklistItem:
        return ChecklistItem(
            id=item_data.get('id', ''),
            name=item_data.get('name', ''),
            state=item_data.get('state', 'incomplete'),
            pos=item_data.get('pos')
        )

    def _convert_to_checklist(self, checklist_data: Dict[str, Any]) -> Checklist:
        check_items = []
        if checklist_data.get('checkItems'):
            for item in checklist_data['checkItems']:
                check_items.append(self._convert_to_checklist_item(item))
        
        return Checklist(
            id=checklist_data.get('id', ''),
            name=checklist_data.get('name', ''),
            checkItems=check_items or None
        )

    def get_card_checklists(self, card_id: str) -> ApiResponse:
        try:
            response = self.client.get_card_checklists(card_id)
            checklists = [self._convert_to_checklist(checklist) for checklist in response]
            return self.prepare_response(checklists, "TrelloChecklistList")
        except Exception as e:
            raise ValueError(f"Error getting checklists: {str(e)}")

    def create_checklist(self, card_id: str, name: str) -> ApiResponse:
        try:
            response = self.client.create_checklist(card_id, name)
            checklist = self._convert_to_checklist(response)
            return self.prepare_response(checklist, "TrelloChecklistDetail")
        except Exception as e:
            raise ValueError(f"Error creating checklist: {str(e)}")

    def create_checklist_item(self, checklist_id: str, name: str, checked: bool = False) -> ApiResponse:
        try:
            response = self.client.create_checklist_item(checklist_id, name, checked)
            item = self._convert_to_checklist_item(response)
            return self.prepare_response(item, None)
        except Exception as e:
            raise ValueError(f"Error creating checklist item: {str(e)}")

    def _convert_to_organization(self, org_data: Dict[str, Any]) -> Organization:
        return Organization(
            id=org_data.get('id', ''),
            name=org_data.get('name', ''),
            displayName=org_data.get('displayName'),
            desc=org_data.get('desc'),
            url=org_data.get('url'),
            website=org_data.get('website')
        )
    
    def _convert_to_member(self, member_data: Dict[str, Any]) -> Member:
        return Member(
            id=member_data.get('id', ''),
            username=member_data.get('username', ''),
            fullName=member_data.get('fullName'),
            avatarUrl=member_data.get('avatarUrl')
        )

    def get_organizations(self, member_id: str = "me") -> ApiResponse:
        try:
            response = self.client.get_organizations(member_id)
            organizations = [self._convert_to_organization(org) for org in response]
            return self.prepare_response(organizations, "TrelloOrganizationList")
        except Exception as e:
            raise ValueError(f"Error getting organizations: {str(e)}")

    def get_organization(self, org_id: str) -> ApiResponse:
        try:
            response = self.client.get_organization(org_id)
            organization = self._convert_to_organization(response)
            return self.prepare_response(organization, "TrelloOrganizationDetail")
        except Exception as e:
            raise ValueError(f"Error getting organization: {str(e)}")
    
    def get_organization_boards(self, org_id: str) -> ApiResponse:
        try:
            response = self.client.get_organization_boards(org_id)
            boards = [self._convert_to_board(board) for board in response]
            return self.prepare_response(boards, "TrelloBoardList")
        except Exception as e:
            raise ValueError(f"Error getting organization boards: {str(e)}")
    
    def get_organization_members(self, org_id: str) -> ApiResponse:
        try:
            response = self.client.get_organization_members(org_id)
            members = [self._convert_to_member(member) for member in response]
            return self.prepare_response(members, "TrelloMemberList")
        except Exception as e:
            raise ValueError(f"Error getting organization members: {str(e)}")
