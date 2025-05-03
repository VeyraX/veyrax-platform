from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

class GetMeParams(BaseModel):
    pass

class BioLink(BaseModel):
    title: Optional[str] = None
    lynx_url: Optional[str] = None
    url: Optional[str] = None
    link_type: Optional[str] = None

class BiographyWithEntities(BaseModel):
    raw_text: str
    entities: List[Any]

class EdgeFollowedBy(BaseModel):
    count: int

class EdgeFollow(BaseModel):
    count: int

class EdgeMutualFollowedBy(BaseModel):
    count: int
    edges: List[Any]

class UserDetails(BaseModel):
    ai_agent_type: Optional[Any] = None
    biography: Optional[str] = None
    bio_links: Optional[List[BioLink]] = None
    fb_profile_biolink: Optional[Any] = None
    biography_with_entities: Optional[BiographyWithEntities] = None
    blocked_by_viewer: Optional[bool] = None
    restricted_by_viewer: Optional[bool] = None
    country_block: Optional[bool] = None
    eimu_id: Optional[str] = None
    external_url: Optional[str] = None
    external_url_linkshimmed: Optional[str] = None
    edge_followed_by: Optional[EdgeFollowedBy] = None
    fbid: Optional[str] = None
    followed_by_viewer: Optional[bool] = None
    edge_follow: Optional[EdgeFollow] = None
    follows_viewer: Optional[bool] = None
    full_name: Optional[str] = None
    group_metadata: Optional[Any] = None
    has_ar_effects: Optional[bool] = None
    has_clips: Optional[bool] = None
    has_guides: Optional[bool] = None
    has_chaining: Optional[bool] = None
    has_channel: Optional[bool] = None
    has_blocked_viewer: Optional[bool] = None
    highlight_reel_count: Optional[int] = None
    has_requested_viewer: Optional[bool] = None
    hide_like_and_view_counts: Optional[bool] = None
    id: Optional[str] = None
    is_business_account: Optional[bool] = None
    is_professional_account: Optional[bool] = None
    is_supervision_enabled: Optional[bool] = None
    is_guardian_of_viewer: Optional[bool] = None
    is_supervised_by_viewer: Optional[bool] = None
    is_supervised_user: Optional[bool] = None
    is_embeds_disabled: Optional[bool] = None
    is_joined_recently: Optional[bool] = None
    guardian_id: Optional[Any] = None
    business_address_json: Optional[Any] = None
    business_contact_method: Optional[str] = None
    business_email: Optional[Any] = None
    business_phone_number: Optional[Any] = None
    business_category_name: Optional[Any] = None
    overall_category_name: Optional[Any] = None
    category_enum: Optional[Any] = None
    category_name: Optional[str] = None
    is_private: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_verified_by_mv4b: Optional[bool] = None
    is_regulated_c18: Optional[bool] = None
    edge_mutual_followed_by: Optional[EdgeMutualFollowedBy] = None
    pinned_channels_list_count: Optional[int] = None
    profile_pic_url: Optional[str] = None
    profile_pic_url_hd: Optional[str] = None
    requested_by_viewer: Optional[bool] = None
    should_show_category: Optional[bool] = None
    should_show_public_contacts: Optional[bool] = None
    show_account_transparency_details: Optional[bool] = None
    transparency_label: Optional[Any] = None
    transparency_product: Optional[Any] = None
    username: str
    connected_fb_page: Optional[Any] = None
    pronouns: Optional[List[Any]] = None

class UserContainer(BaseModel):
    user: UserDetails

class UserResponse(BaseModel):
    data: UserContainer
    status: str

class GetUserDetailsParams(BaseModel):
    username: str = Field(..., description="Instagram username")

class GetUserDetailsResponse(BaseModel):
    data: UserResponse

class PostAuthor(BaseModel):
    id: str
    username: str
    profile_pic_url: Optional[str] = None

class ImageVersion(BaseModel):
    height: int
    width: int
    url: str

class PostCaption(BaseModel):
    text: str
    pk: Optional[str] = None
    user_id: Optional[str] = None

class PostItem(BaseModel):
    pk: str
    id: str
    code: Optional[str] = None
    media_type: int
    taken_at: int
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    caption: Optional[PostCaption] = None
    user: PostAuthor
    original_width: Optional[int] = None
    original_height: Optional[int] = None

class PostList(BaseModel):
    items: List[PostItem]
    num_results: int
    more_available: bool
    cursor: Optional[str] = None

class PostResponse(BaseModel):
    items: List[PostItem]
    num_results: int
    more_available: bool
    cursor: Optional[str] = None

class GetUserPostsParams(BaseModel):
    username: str = Field(..., description="Instagram username")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")

class GetUserPostsResponse(BaseModel):
    data: PostResponse

class UserListItem(BaseModel):
    pk: str
    id: str
    username: str
    full_name: Optional[str] = None
    is_private: Optional[bool] = None
    profile_pic_url: Optional[str] = None
    is_verified: Optional[bool] = None
    has_anonymous_profile_picture: Optional[bool] = None
    latest_reel_media: Optional[int] = None

class UserListResponse(BaseModel):
    users: List[UserListItem]
    big_list: bool
    page_size: int
    next_max_id: Optional[str] = None
    has_more: bool
    status: str

class GetUserFollowingParams(BaseModel):
    user_id: str = Field(..., description="Instagram user ID")
    count: Optional[int] = Field(20, description="Number of users to retrieve")
    cursor: Optional[str] = Field(None, description="Next max ID for pagination")

class GetUserFollowersParams(BaseModel):
    user_id: str = Field(..., description="Instagram user ID")
    count: Optional[int] = Field(20, description="Number of users to retrieve")
    cursor: Optional[str] = Field(None, description="Next max ID for pagination")

class GetUserFollowingResponse(BaseModel):
    data: UserListResponse
    component: Optional[Dict[str, Any]] = None

class GetUserFollowersResponse(BaseModel):
    data: UserListResponse
    component: Optional[Dict[str, Any]] = None

class VideoVersion(BaseModel):
    width: int
    height: int
    url: str
    type: Optional[int] = None

class ClipsMetadata(BaseModel):
    audio_type: Optional[str] = None
    music_info: Optional[Dict[str, Any]] = None
    original_sound_info: Optional[Dict[str, Any]] = None

class UserTag(BaseModel):
    user: Dict[str, Any]
    position: List[float]

class UserTags(BaseModel):
    in_: Optional[List[UserTag]] = Field(None, alias="in")

class PostDetailItem(BaseModel):
    pk: str
    id: str
    code: str
    taken_at: int
    media_type: int
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    caption: Optional[Dict[str, Any]] = None
    user: Dict[str, Any]
    video_versions: Optional[List[VideoVersion]] = None
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    is_paid_partnership: Optional[bool] = None
    clips_metadata: Optional[ClipsMetadata] = None
    usertags: Optional[UserTags] = None
    has_audio: Optional[bool] = None
    has_liked: Optional[bool] = None

class PostDetailContainer(BaseModel):
    items: List[PostDetailItem]

class PostDetailData(BaseModel):
    data: Dict[str, PostDetailContainer]

class GetPostDetailsParams(BaseModel):
    shortcode: str = Field(..., description="Instagram post shortcode")

class GetPostDetailsResponse(BaseModel):
    data: PostDetailData
    component: Optional[Dict[str, Any]] = None

class CommentUser(BaseModel):
    pk: str
    username: str
    full_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_private: Optional[bool] = None
    is_verified: Optional[bool] = None

class Comment(BaseModel):
    pk: str
    user_id: str
    text: str
    created_at: int
    comment_like_count: Optional[int] = None
    user: CommentUser
    child_comment_count: Optional[int] = None
    has_liked_comment: Optional[bool] = None
    has_translation: Optional[bool] = None

class PostCaption(BaseModel):
    pk: Optional[str] = None
    user_id: Optional[str] = None
    text: str
    created_at: Optional[int] = None
    user: Optional[CommentUser] = None
    is_covered: Optional[bool] = None

class PostCommentsResponse(BaseModel):
    comment_likes_enabled: bool
    comments: List[Comment]
    comment_count: int
    caption: Optional[PostCaption] = None
    has_more_comments: bool
    status: str

class GetPostCommentsParams(BaseModel):
    pk: str = Field(..., description="Instagram post ID")
    next_min_id: Optional[str] = Field(None, description="Token for pagination")

class GetPostCommentsResponse(BaseModel):
    data: PostCommentsResponse
    component: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    data: Union[UserResponse, PostResponse, UserListResponse, PostDetailData, PostCommentsResponse]
    component: Optional[Dict[str, Any]] = None