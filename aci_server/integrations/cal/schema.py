from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal


# Common models
class Host(BaseModel):
    id: int
    name: str
    email: str
    username: str
    timeZone: str


class EventType(BaseModel):
    id: int
    slug: str


class Attendee(BaseModel):
    name: str
    email: str
    timeZone: str
    phoneNumber: Optional[str] = None
    language: Optional[str] = None


# Location models
class AddressLocation(BaseModel):
    type: Literal["address"]
    value: Optional[str] = None


class LinkLocation(BaseModel):
    type: Literal["link"]
    value: Optional[str] = None


class PhoneLocation(BaseModel):
    type: Literal["phone"]
    value: Optional[str] = None


class GoogleMeetLocation(BaseModel):
    type: Literal["googlemeet"]
    value: Optional[str] = None


class ZoomLocation(BaseModel):
    type: Literal["zoom"]
    value: Optional[str] = None


class JitsiLocation(BaseModel):
    type: Literal["jitsi"]
    value: Optional[str] = None


class TeamsLocation(BaseModel):
    type: Literal["teams"]
    value: Optional[str] = None


class DailyLocation(BaseModel):
    type: Literal["daily"]
    value: Optional[str] = None


# Organization model
class Organization(BaseModel):
    isPlatform: bool
    id: int


# User profile model
class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    timeFormat: Optional[int] = None
    defaultScheduleId: Optional[int] = None
    weekStart: Optional[str] = None
    timeZone: Optional[str] = None
    organizationId: Optional[int] = None
    organization: Optional[Organization] = None


# Schedule models
class ScheduleAvailability(BaseModel):
    days: List[str]
    startTime: str
    endTime: str


class ScheduleOverride(BaseModel):
    date: str
    startTime: str
    endTime: str


class Schedule(BaseModel):
    id: int
    ownerId: int
    name: str
    timeZone: str
    availability: List[ScheduleAvailability]
    isDefault: bool
    overrides: Optional[List[ScheduleOverride]] = None


class ScheduleList(BaseModel):
    schedules: List[Schedule]


# Booking models
class Booking(BaseModel):
    id: int
    uid: str
    title: str
    description: Optional[str] = None
    hosts: List[Host]
    status: str
    cancellationReason: Optional[str] = None
    cancelledByEmail: Optional[str] = None
    reschedulingReason: Optional[str] = None
    rescheduledByEmail: Optional[str] = None
    rescheduledFromUid: Optional[str] = None
    start: str
    end: str
    duration: int
    eventTypeId: Optional[int] = None
    eventType: Optional[EventType] = None
    meetingUrl: Optional[str] = None
    location: Optional[str] = None
    absentHost: Optional[bool] = None
    createdAt: str
    updatedAt: str
    metadata: Optional[Dict[str, Any]] = None
    rating: Optional[int] = None
    icsUid: Optional[str] = None
    attendees: List[Attendee]
    guests: Optional[List[str]] = None
    bookingFieldsResponses: Optional[Dict[str, Any]] = None


class BookingList(BaseModel):
    bookings: List[Booking]


# Input parameters
class GetBookingsParams(BaseModel):
    status: Optional[str] = None
    attendeeEmail: Optional[str] = None
    attendeeName: Optional[str] = None
    eventTypeIds: Optional[str] = None
    eventTypeId: Optional[str] = None
    teamsIds: Optional[str] = None
    teamId: Optional[str] = None
    afterStart: Optional[str] = None
    beforeEnd: Optional[str] = None
    afterCreatedAt: Optional[str] = None
    beforeCreatedAt: Optional[str] = None
    afterUpdatedAt: Optional[str] = None
    beforeUpdatedAt: Optional[str] = None
    sortStart: Optional[Literal["asc", "desc"]] = None
    sortEnd: Optional[Literal["asc", "desc"]] = None
    sortCreated: Optional[Literal["asc", "desc"]] = None
    sortUpdatedAt: Optional[Literal["asc", "desc"]] = None
    take: Optional[int] = None
    skip: Optional[int] = None


class GetBookingParams(BaseModel):
    bookingUid: str


class CreateBookingAttendee(BaseModel):
    name: str
    email: str
    timeZone: str
    phoneNumber: Optional[str] = None
    language: Optional[str] = None


class CreateBookingParams(BaseModel):
    start: str = Field(..., description="The start time of the booking in ISO 8601 format in UTC timezone")
    attendee: CreateBookingAttendee
    lengthInMinutes: Optional[int] = None
    eventTypeId: Optional[int] = None
    eventTypeSlug: Optional[str] = None
    username: Optional[str] = None
    organizationSlug: Optional[str] = None
    guests: Optional[List[str]] = None
    meetingUrl: Optional[str] = None
    location: Optional[Union[
        AddressLocation,
        LinkLocation,
        PhoneLocation,
        GoogleMeetLocation,
        ZoomLocation,
        JitsiLocation,
        TeamsLocation,
        DailyLocation
    ]] = None
    metadata: Optional[Dict[str, Any]] = None
    bookingFieldsResponses: Optional[Dict[str, Any]] = None


class RescheduleBookingParams(BaseModel):
    bookingUid: str
    start: str = Field(..., description="Start time in ISO 8601 format for the new booking")
    rescheduledBy: Optional[str] = None
    reschedulingReason: Optional[str] = None


class CancelBookingParams(BaseModel):
    bookingUid: str
    cancellationReason: Optional[str] = None
    cancelSubsequentBookings: Optional[bool] = None


class GetScheduleParams(BaseModel):
    scheduleId: int


class UpdateScheduleParams(BaseModel):
    scheduleId: int
    name: Optional[str] = None
    timeZone: Optional[str] = None
    availability: Optional[List[ScheduleAvailability]] = None
    isDefault: Optional[bool] = None
    overrides: Optional[List[ScheduleOverride]] = None

class GetSchedulesParams(BaseModel):
    pass


class GetProfileParams(BaseModel):
    pass


# Response classes
class GetBookingsResponse(BaseModel):
    data: BookingList


class GetBookingResponse(BaseModel):
    data: Booking


class CreateBookingResponse(BaseModel):
    data: Booking


class RescheduleBookingResponse(BaseModel):
    data: Booking


class CancelBookingResponse(BaseModel):
    data: Booking


class GetProfileResponse(BaseModel):
    data: UserProfile


class GetSchedulesResponse(BaseModel):
    data: ScheduleList


class GetScheduleResponse(BaseModel):
    data: Schedule


class UpdateScheduleResponse(BaseModel):
    data: Schedule


class ValidateKeyResponse(BaseModel):
    valid: bool
    message: str


# Main API response model
class ApiResponse(BaseModel):
    data: Union[Booking, BookingList, UserProfile, Schedule, ScheduleList]
    component: Optional[Dict[str, Any]] = None
