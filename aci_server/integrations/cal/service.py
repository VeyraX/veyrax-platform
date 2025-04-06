from typing import Dict, Any, Optional, List, Union
import os
from .client import CalClient
from .schema import (
    GetBookingsParams,
    GetBookingParams,
    CreateBookingParams,
    RescheduleBookingParams,
    CancelBookingParams,
    GetScheduleParams,
    UpdateScheduleParams,
    GetEventTypesParams,
    GetBookingsResponse,
    GetBookingResponse,
    CreateBookingResponse,
    RescheduleBookingResponse,
    CancelBookingResponse,
    GetProfileResponse,
    GetSchedulesResponse,
    GetScheduleResponse,
    UpdateScheduleResponse,
    GetEventTypesResponse,
    Booking,
    BookingList,
    UserProfile,
    Schedule,
    ScheduleList,
    EventTypeList,
    DetailedEventType,
    ApiResponse
)
from ..common.component_handler import load_components, prepare_components_auto

class CalService:
    def __init__(self, client: CalClient):
        self.client = client
        self.components_data = self._load_components()
    
    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "cal"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_bookings(self, params: GetBookingsParams) -> ApiResponse:
        processed_params = self._process_get_bookings_params(params)
        response = self.client.get_bookings(processed_params)
        
        if "data" in response and isinstance(response["data"], list):
            booking_list = BookingList(bookings=response["data"])
            return self.prepare_response(booking_list, "BookingList")
        
        return self.prepare_response(BookingList(bookings=[]), "BookingList")
    
    def get_booking(self, params: GetBookingParams) -> ApiResponse:
        response = self.client.get_booking(params.bookingUid)
        
        if "data" in response and not isinstance(response["data"], list):
            booking = Booking(**response["data"])
            return self.prepare_response(booking, "Booking")
        
        if "data" in response and isinstance(response["data"], list):
            booking_list = BookingList(bookings=response["data"])
            return self.prepare_response(booking_list, "BookingList")
        
        return self.prepare_response(Booking(), "Booking")
    
    def create_booking(self, params: CreateBookingParams) -> ApiResponse:
        processed_params = self._process_create_booking_params(params)
        response = self.client.create_booking(processed_params)
        
        if "data" in response:
            booking = Booking(**response["data"])
            return self.prepare_response(booking, "Booking")
        
        return self.prepare_response(Booking(), "Booking")
    
    def reschedule_booking(self, params: RescheduleBookingParams) -> ApiResponse:
        booking_uid = params.bookingUid
        processed_params = self._process_reschedule_booking_params(params)
        response = self.client.reschedule_booking(booking_uid, processed_params)
        
        if "data" in response:
            booking = Booking(**response["data"])
            return self.prepare_response(booking, "Booking")
        
        return self.prepare_response(Booking(), "Booking")
    
    def cancel_booking(self, params: CancelBookingParams) -> ApiResponse:
        booking_uid = params.bookingUid
        processed_params = self._process_cancel_booking_params(params)
        response = self.client.cancel_booking(booking_uid, processed_params)
        
        if "data" in response:
            if isinstance(response["data"], list):
                booking_list = BookingList(bookings=response["data"])
                return self.prepare_response(booking_list, "BookingList")
            else:
                booking = Booking(**response["data"])
                return self.prepare_response(booking, "Booking")
        
        return self.prepare_response(Booking(), "Booking")
    
    def get_profile(self) -> ApiResponse:
        response = self.client.get_me()
        
        if "data" in response:
            profile = UserProfile(**response["data"])
            return self.prepare_response(profile, "UserProfile")
        
        return self.prepare_response(UserProfile(), "UserProfile")
    
    def get_schedules(self) -> ApiResponse:
        response = self.client.get_schedules()
        
        if "data" in response and isinstance(response["data"], list):
            schedule_list = ScheduleList(schedules=response["data"])
            return self.prepare_response(schedule_list, "ScheduleList")
        
        return self.prepare_response(ScheduleList(schedules=[]), "ScheduleList")
    
    def get_schedule(self, params: GetScheduleParams) -> ApiResponse:
        response = self.client.get_schedule(params.scheduleId)
        
        if "data" in response:
            schedule = Schedule(**response["data"])
            return self.prepare_response(schedule, "Schedule")
        
        return self.prepare_response(Schedule(), "Schedule")
    
    def update_schedule(self, params: UpdateScheduleParams) -> ApiResponse:
        schedule_id = params.scheduleId
        processed_params = self._process_update_schedule_params(params)
        response = self.client.update_schedule(schedule_id, processed_params)
        
        if "data" in response:
            schedule = Schedule(**response["data"])
            return self.prepare_response(schedule, "Schedule")
        
        return self.prepare_response(Schedule(), "Schedule")
    
    def get_event_types(self, params: GetEventTypesParams) -> ApiResponse:
        processed_params = self._process_get_event_types_params(params)
        response = self.client.get_event_types(processed_params)
        
        if "data" in response and isinstance(response["data"], list):
            event_type_list = EventTypeList(eventTypes=response["data"])
            return self.prepare_response(event_type_list, "EventTypeList")
        
        return self.prepare_response(EventTypeList(eventTypes=[]), "EventTypeList")

    def _process_get_bookings_params(self, params: GetBookingsParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
    
    def _process_create_booking_params(self, params: CreateBookingParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
    
    def _process_reschedule_booking_params(self, params: RescheduleBookingParams) -> Dict[str, Any]:
        return params.model_dump(exclude={"bookingUid"}, exclude_none=True)
    
    def _process_cancel_booking_params(self, params: CancelBookingParams) -> Dict[str, Any]:
        return params.model_dump(exclude={"bookingUid"}, exclude_none=True)
    
    def _process_update_schedule_params(self, params: UpdateScheduleParams) -> Dict[str, Any]:
        return params.model_dump(exclude={"scheduleId"}, exclude_none=True)
    
    def _process_get_event_types_params(self, params: GetEventTypesParams) -> Dict[str, Any]:
        return params.model_dump(exclude_none=True)
