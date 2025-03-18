from typing import Dict, Any, List, Optional
from .client import DubClient
from .schema import (
    CreateLinkParams,
    UpdateLinkParams,
    UpsertLinkParams,
    DeleteLinkParams,
    GetLinkParams,
    GetLinksParams,
    Link,
    LinkResponse,
    LinksResponse,
    ApiResponse,
    LinkList,
    EventList,
    Event,
    Customer,
    CustomerList,
    GetCustomerParams,
    UpdateCustomerParams,
    DeleteCustomerParams,
    TrackLeadParams,
    TrackSaleParams,
    CreateTagParams,
    UpdateTagParams,
    Tag,
    TagList,
    Domain,
    DomainList,
    CreateDomainParams,
    UpdateDomainParams,
    DeleteDomainParams,
    Workspace,
    GetWorkspaceParams,
    UpdateWorkspaceParams,
    BulkUpdateLinksParams
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class DubService:
    def __init__(self, client: DubClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "dub"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def create_link(self, params: CreateLinkParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.create_link(processed_params)
        return ApiResponse(data=Link(**response))

    def update_link(self, link_id: str, params: UpdateLinkParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.update_link(link_id, processed_params)
        return ApiResponse(data=Link(**response))

    def upsert_link(self, params: UpsertLinkParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.upsert_link(processed_params)
        return ApiResponse(data=Link(**response))

    def delete_link(self, link_id: str) -> ApiResponse:
        response = self.client.delete_link(link_id)
        return ApiResponse(data=Link(**response))

    def get_link_info(self, link_id: Optional[str] = None) -> ApiResponse:
        response = self.client.get_link_info(link_id)
        return ApiResponse(data=Link(**response))

    def get_links(self) -> ApiResponse:
        response = self.client.get_links()
        links = [Link(**link) for link in response]
        return ApiResponse(data=LinkList(items=links))

    def get_links_count(self) -> ApiResponse:
        response = self.client.get_links_count()
        if isinstance(response, int):
            count = response
        else:
            count = response.get("count", 0)
        return ApiResponse(data={"count": count})

    def bulk_create_links(self, links: List[CreateLinkParams]) -> ApiResponse:
        processed_params = [self._process_params(link) for link in links]
        response = self.client.bulk_create_links(processed_params)
        links_data = [Link(**link) for link in response]
        return ApiResponse(data=LinkList(items=links_data))

    def bulk_update_links(self, params: BulkUpdateLinksParams) -> ApiResponse:
        payload = params.model_dump(exclude_none=True)
        response = self.client.bulk_update_links(payload)
        links_data = [Link(**link) for link in response]
        return ApiResponse(data=LinkList(items=links_data))

    def bulk_delete_links(self, link_ids: List[str]) -> ApiResponse:
        response = self.client.bulk_delete_links(link_ids)
        return ApiResponse(data={"deletedCount": response.get("deletedCount", 0)})

    def get_qr_code(self, link_id: Optional[str] = None) -> ApiResponse:
        response = self.client.get_qr_code(link_id)
        return ApiResponse(data=response)

    def get_analytics(self) -> ApiResponse:
        response = self.client.get_analytics()
        return ApiResponse(data=response)

    def get_events(self) -> ApiResponse:
        response = self.client.get_events()
        events = [Event(**event) for event in response]
        return ApiResponse(data=EventList(items=events))

    def get_customer(self, customer_id: str) -> ApiResponse:
        response = self.client.get_customer(customer_id)
        return ApiResponse(data=Customer(**response))

    def get_customers(self) -> ApiResponse:
        response = self.client.get_customers()
        customers = [Customer(**customer) for customer in response]
        return ApiResponse(data=CustomerList(items=customers))

    def update_customer(self, customer_id: str, params: UpdateCustomerParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.update_customer(customer_id, processed_params)
        return ApiResponse(data=Customer(**response))

    def delete_customer(self, customer_id: str) -> ApiResponse:
        response = self.client.delete_customer(customer_id)
        return ApiResponse(data=response)

    def track_lead(self, params: TrackLeadParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.track_lead(processed_params)
        return ApiResponse(data=response)

    def track_sale(self, params: TrackSaleParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.track_sale(processed_params)
        return ApiResponse(data=response)

    def create_tag(self, params: CreateTagParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.create_tag(processed_params)
        return ApiResponse(data=Tag(**response))

    def get_tags(self) -> ApiResponse:
        response = self.client.get_tags()
        tags = [Tag(**tag) for tag in response]
        return ApiResponse(data=TagList(items=tags))

    def update_tag(self, tag_id: str, params: UpdateTagParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.update_tag(tag_id, processed_params)
        return ApiResponse(data=Tag(**response))

    def _process_params(self, params) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True, exclude={"link_id"})

    # Domain management methods
    def create_domain(self, params: CreateDomainParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.create_domain(processed_params)
        return ApiResponse(data=Domain(**response))

    def update_domain(self, slug: str, params: UpdateDomainParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.update_domain(slug, processed_params)
        return ApiResponse(data=Domain(**response))

    def delete_domain(self, slug: str) -> ApiResponse:
        response = self.client.delete_domain(slug)
        return ApiResponse(data=response)

    def get_domains(self) -> ApiResponse:
        response = self.client.get_domains()
        domains = [Domain(**domain) for domain in response]
        return ApiResponse(data=DomainList(items=domains))

    # Workspace management methods
    def get_workspace(self, id_or_slug: str) -> ApiResponse:
        response = self.client.get_workspace(id_or_slug)
        return ApiResponse(data=Workspace(**response))

    def update_workspace(self, id_or_slug: str, params: UpdateWorkspaceParams) -> ApiResponse:
        processed_params = self._process_params(params)
        response = self.client.update_workspace(id_or_slug, processed_params)
        return ApiResponse(data=Workspace(**response))
