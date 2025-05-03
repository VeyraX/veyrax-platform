from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Any, Optional, Union, Literal


class LocationInfo(BaseModel):
    label: str
    uid: str
    city_id: int
    timezone: str


class LocationList(BaseModel):
    results: List[LocationInfo]


class SearchLocationsParams(BaseModel):
    query: str = Field(..., description="Search query for locations")


class SearchLocationsResponse(BaseModel):
    data: LocationList


class PostAuthor(BaseModel):
    id: str
    name: str
    url: str
    profile_picture_url: str


class Reactions(BaseModel):
    angry: Optional[int] = 0
    care: Optional[int] = 0
    haha: Optional[int] = 0
    like: Optional[int] = 0
    love: Optional[int] = 0
    sad: Optional[int] = 0
    wow: Optional[int] = 0


class ImagePreview(BaseModel):
    image_file_uri: str
    url: str


class PostResult(BaseModel):
    post_id: str
    type: str
    url: str
    message: Optional[str] = None
    timestamp: int
    comments_count: int
    reactions_count: int
    reshare_count: int
    reactions: Reactions
    author: PostAuthor
    image: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    album_preview: Optional[List[ImagePreview]] = None
    video_files: Optional[Dict[str, Any]] = None
    video_thumbnail: Optional[Dict[str, Any]] = None
    external_url: Optional[str] = None
    attached_event: Optional[Dict[str, Any]] = None
    attached_post: Optional[Dict[str, Any]] = None
    attached_post_url: Optional[str] = None


class PostList(BaseModel):
    results: List[PostResult]
    cursor: Optional[str] = None


class SearchPostsParams(BaseModel):
    query: str = Field(..., description="Search query for posts")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    location_uid: Optional[str] = Field(None, description="Location UID to filter posts by location")
    start_date: Optional[str] = Field(None, description="Start date for filtering posts (mm/dd/yyyy)")
    end_date: Optional[str] = Field(None, description="End date for filtering posts (mm/dd/yyyy)")


class SearchPostsResponse(BaseModel):
    data: PostList


# Search Places Models
class PlaceImage(BaseModel):
    uri: str
    width: int
    height: int
    scale: int


class PlaceResult(BaseModel):
    type: str
    profile_url: str
    url: str
    image: PlaceImage
    name: str
    facebook_id: str
    is_verified: bool


class PlaceList(BaseModel):
    results: List[PlaceResult]
    cursor: Optional[str] = None


class SearchPlacesParams(BaseModel):
    query: str = Field(..., description="Search query for places")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")


class SearchPlacesResponse(BaseModel):
    data: PlaceList


class PageImage(BaseModel):
    uri: str
    width: int
    height: int
    scale: int


class PageResult(BaseModel):
    type: str
    profile_url: str
    url: str
    image: PageImage
    name: str
    facebook_id: str
    is_verified: bool


class PageList(BaseModel):
    results: List[PageResult]
    cursor: Optional[str] = None


class SearchPagesParams(BaseModel):
    query: str = Field(..., description="Search query for pages")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    location_uid: Optional[str] = Field(None, description="Location UID to filter pages by location")


class SearchPagesResponse(BaseModel):
    data: PageList


# Search Events Models
class EventResult(BaseModel):
    type: str
    event_id: str
    title: str
    url: str


class EventList(BaseModel):
    results: List[EventResult]
    cursor: Optional[str] = None


class SearchEventsParams(BaseModel):
    query: str = Field(..., description="Search query for events")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    location_uid: Optional[str] = Field(None, description="Location UID to filter events by location")
    start_date: Optional[str] = Field(None, description="Start date for filtering events (mm/dd/yyyy)")
    end_date: Optional[str] = Field(None, description="End date for filtering events (mm/dd/yyyy)")


class SearchEventsResponse(BaseModel):
    data: EventList


class DelegatePage(BaseModel):
    is_business_page_active: bool
    id: str


class PageDetails(BaseModel):
    name: str
    type: str
    page_id: str
    url: str
    image: str
    intro: Optional[str] = None
    likes: Optional[int] = None
    followers: Optional[int] = None
    categories: Optional[List[str]] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    services: Optional[str] = None
    price_range: Optional[str] = None
    website: Optional[str] = None
    delegate_page: Optional[DelegatePage] = None
    cover_image: Optional[str] = None
    verified: Optional[bool] = None


class PageDetailsContainer(BaseModel):
    results: PageDetails


class GetPageDetailsParams(BaseModel):
    url: str = Field(..., description="URL of the Facebook page")


class GetPageDetailsResponse(BaseModel):
    data: PageDetailsContainer


class PageIdResult(BaseModel):
    page_id: str


class GetPageIdParams(BaseModel):
    url: str = Field(..., description="URL of the Facebook page")


class GetPageIdResponse(BaseModel):
    data: PageIdResult


class GetPagePostsParams(BaseModel):
    page_id: str = Field(..., description="ID of the Facebook page")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    start_date: Optional[str] = Field(None, description="Start date for filtering posts (yyyy-mm-dd)")
    end_date: Optional[str] = Field(None, description="End date for filtering posts (yyyy-mm-dd)")


class GetPagePostsResponse(BaseModel):
    data: PostList


class ReviewAuthorProfilePicture(BaseModel):
    uri: str
    width: int
    height: int
    scale: int


class ReviewAuthor(BaseModel):
    id: str
    name: str
    url: str
    profile_picture: ReviewAuthorProfilePicture
    is_additional_profile_plus: bool
    delegated_page: Optional[Any] = None
    work_info: Optional[Any] = None


class ReviewResult(BaseModel):
    type: str
    post_id: str
    recommend: bool
    message: str
    author: ReviewAuthor
    reactions_count: int
    share: int
    photos: List[Any]
    tags: List[Any]


class ReviewList(BaseModel):
    results: List[ReviewResult]
    cursor: Optional[str] = None


class GetPageReviewsParams(BaseModel):
    page_id: str = Field(..., description="ID of the Facebook page")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")


class GetPageReviewsResponse(BaseModel):
    data: ReviewList


# Post Comments Models
class CommentAuthor(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    url: Optional[str] = None


class CommentResult(BaseModel):
    type: str
    comment_id: str
    legacy_comment_id: str
    depth: int
    created_time: int
    message: str
    author: CommentAuthor
    replies_count: int
    reactions_count: str
    expansion_token: Optional[str] = None


class CommentList(BaseModel):
    results: List[CommentResult]
    cursor: Optional[str] = None


class GetPostCommentsParams(BaseModel):
    post_id: str = Field(..., description="ID of the Facebook post")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")


class GetPostCommentsResponse(BaseModel):
    data: CommentList


class PostDetailsContainer(BaseModel):
    results: PostResult


class GetPostDetailsParams(BaseModel):
    post_id: str = Field(..., description="ID of the Facebook post")


class GetPostDetailsResponse(BaseModel):
    data: PostDetailsContainer


class GetGroupPostsParams(BaseModel):
    group_id: str = Field(..., description="ID of the Facebook group")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    sorting_order: Optional[Literal["CHRONOLOGICAL", "TOP POSTS"]] = Field(None, description="Sorting order for posts")

class GroupPostList(BaseModel):
    posts: List[PostResult]
    cursor: Optional[str] = None

class GetGroupPostsResponse(BaseModel):
    data: GroupPostList

# Group Details Models
class GroupLocation(BaseModel):
    name: str
    id: str

class GroupCoverPhoto(BaseModel):
    uri: str
    width: int
    height: int

class GroupDetails(BaseModel):
    id: str
    name: str
    url: str
    description: Optional[str] = None
    group_location: Optional[GroupLocation] = None
    privacy: Optional[str] = None
    has_questions: Optional[bool] = None
    cover_photo: Optional[GroupCoverPhoto] = None
    members_count: Optional[int] = None

class GroupDetailsContainer(BaseModel):
    group_details: GroupDetails

class GetGroupDetailsParams(BaseModel):
    url: str = Field(..., description="URL of the Facebook group")

class GetGroupDetailsResponse(BaseModel):
    data: GroupDetailsContainer

class GroupIdResult(BaseModel):
    group_id: str

class GetGroupIdParams(BaseModel):
    url: str = Field(..., description="URL of the Facebook group")

class GetGroupIdResponse(BaseModel):
    data: GroupIdResult

class GetProfilePostsParams(BaseModel):
    profile_id: str = Field(..., description="ID of the Facebook profile")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    start_date: Optional[str] = Field(None, description="Start date for filtering posts (yyyy-mm-dd)")
    end_date: Optional[str] = Field(None, description="End date for filtering posts (yyyy-mm-dd)")

class ProfilePostList(BaseModel):
    results: List[PostResult]
    cursor: Optional[str] = None

class GetProfilePostsResponse(BaseModel):
    data: ProfilePostList

class AboutPublicItem(BaseModel):
    icon: Optional[Dict[str, Any]] = None
    text: str

class ProfileAbout(RootModel):
    root: Dict[str, Any] = Field(default_factory=dict)

class ProfileDetails(BaseModel):
    name: str
    profile_id: str
    url: str
    image: str
    intro: Optional[str] = None
    cover_image: Optional[str] = None
    gender: Optional[str] = None
    about: Optional[ProfileAbout] = None
    about_public: Optional[List[AboutPublicItem]] = None

class ProfileDetailsContainer(BaseModel):
    profile: ProfileDetails

class GetProfileDetailsIdParams(BaseModel):
    profile_id: str = Field(..., description="ID of the Facebook profile")

class GetProfileDetailsUrlParams(BaseModel):
    url: str = Field(..., description="URL of the Facebook profile")

class GetProfileDetailsResponse(BaseModel):
    data: ProfileDetailsContainer

class ProfileIdResult(BaseModel):
    profile_id: str

class GetProfileIdParams(BaseModel):
    url: str = Field(..., description="URL of the Facebook profile")

class GetProfileIdResponse(BaseModel):
    data: ProfileIdResult

class GetMeParams(BaseModel):
    pass

class GetMeResponse(BaseModel):
    data: ProfileDetailsContainer
    
class ApiResponse(BaseModel):
    data: Union[
        LocationList, 
        PostList, 
        PlaceList, 
        PageList, 
        EventList, 
        PageDetailsContainer, 
        PageIdResult, 
        ReviewList,
        CommentList,
        PostDetailsContainer,
        GroupPostList,
        GroupDetailsContainer,
        GroupIdResult,
        ProfilePostList,
        ProfileDetailsContainer,
        ProfileIdResult
    ]
    component: Optional[Dict[str, Any]] = None