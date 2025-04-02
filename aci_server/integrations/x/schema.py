from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union

class GetUserProfileParams(BaseModel):
    screenname: str = Field(..., description="Twitter username/screenname without the @ symbol")
    rest_id: Optional[str] = Field(None, description="Twitter user ID for more precise lookup")

class UserProfileData(BaseModel):
    profile: Optional[str] = Field(None, description="Profile URL")
    rest_id: Optional[str] = Field(None, description="Twitter user ID")
    avatar: Optional[str] = Field(None, description="Profile avatar URL")
    desc: Optional[str] = Field(None, description="User bio/description")
    name: Optional[str] = Field(None, description="Display name")
    friends: Optional[int] = Field(None, description="Following count")
    sub_count: Optional[int] = Field(None, description="Followers count")
    id: Optional[str] = Field(None, description="User identifier")

class UserProfileResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: UserProfileData

# Timeline endpoint
class GetUserTimelineParams(BaseModel):
    screenname: str = Field(..., description="Twitter username/screenname without the @ symbol")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")


class UserTimelineData(BaseModel):
    timeline: List[Dict[str, Any]] = Field([], description="List of timeline items/tweets")
    user: Optional[UserProfileData] = Field(None, description="User profile information")

class UserTimelineResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: UserTimelineData

# Following endpoint
class GetUserFollowingParams(BaseModel):
    screenname: str = Field(..., description="Twitter username/screenname without the @ symbol")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")

class FollowingUser(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID")
    screen_name: Optional[str] = Field(None, description="Screen name/username")
    description: Optional[str] = Field(None, description="User description/bio")
    profile_image: Optional[str] = Field(None, description="Profile image URL")
    statuses_count: Optional[int] = Field(None, description="Number of tweets")
    followers_count: Optional[int] = Field(None, description="Number of followers")
    friends_count: Optional[int] = Field(None, description="Number of following")
    media_count: Optional[int] = Field(None, description="Number of media posts")
    name: Optional[str] = Field(None, description="Display name")

class UserFollowingData(BaseModel):
    following: List[FollowingUser] = Field([], description="List of users being followed")
    next_cursor: Optional[str] = Field(None, description="Cursor for the next page of results")

class UserFollowingResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: UserFollowingData

# Followers endpoint
class GetUserFollowersParams(BaseModel):
    screenname: str = Field(..., description="Twitter username/screenname without the @ symbol")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")

class UserFollowersData(BaseModel):
    followers_count: Optional[int] = Field(None, description="Total number of followers")
    followers: List[FollowingUser] = Field([], description="List of follower users")
    next_cursor: Optional[str] = Field(None, description="Cursor for the next page of results")
    status: Optional[str] = Field(None, description="Status of the request")

class UserFollowersResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: UserFollowersData

# Tweet endpoint
class GetTweetParams(BaseModel):
    id: str = Field(..., description="Tweet ID to retrieve")

class TweetAuthor(BaseModel):
    rest_id: Optional[str] = Field(None, description="Author's user ID")
    name: Optional[str] = Field(None, description="Author's display name")
    screen_name: Optional[str] = Field(None, description="Author's username/screen name")
    image: Optional[str] = Field(None, description="Author's profile image URL")
    blue_verified: Optional[bool] = Field(None, description="Whether the author is verified with Twitter Blue")

class TweetMedia(BaseModel):
    video: Optional[List[Dict[str, Any]]] = Field(None, description="Video media in the tweet")

class TweetData(BaseModel):
    likes: Optional[int] = Field(None, description="Number of likes")
    created_at: Optional[str] = Field(None, description="Tweet creation timestamp")
    text: Optional[str] = Field(None, description="Tweet text content")
    retweets: Optional[int] = Field(None, description="Number of retweets")
    bookmarks: Optional[int] = Field(None, description="Number of bookmarks")
    quotes: Optional[int] = Field(None, description="Number of quote tweets")
    replies: Optional[int] = Field(None, description="Number of replies")
    lang: Optional[str] = Field(None, description="Tweet language code")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    author: Optional[TweetAuthor] = Field(None, description="Tweet author information")
    media: Optional[TweetMedia] = Field(None, description="Media content in the tweet")
    id: Optional[str] = Field(None, description="Tweet ID")

class TweetResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: TweetData

# Tweet Retweets endpoint
class GetTweetRetweetsParams(BaseModel):
    id: str = Field(..., description="Tweet ID to get retweets for")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")

class RetweetUser(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID")
    screen_name: Optional[str] = Field(None, description="Screen name/username")
    description: Optional[str] = Field(None, description="User description/bio")
    profile_image: Optional[str] = Field(None, description="Profile image URL")
    statuses_count: Optional[int] = Field(None, description="Number of tweets")
    followers_count: Optional[int] = Field(None, description="Number of followers")
    friends_count: Optional[int] = Field(None, description="Number of following")
    media_count: Optional[int] = Field(None, description="Number of media posts")
    name: Optional[str] = Field(None, description="Display name")

class TweetRetweetsData(BaseModel):
    retweets: List[RetweetUser] = Field([], description="List of users who retweeted")
    next_cursor: Optional[str] = Field(None, description="Cursor for the next page of results")

class TweetRetweetsResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: TweetRetweetsData



class SearchTweetsParams(BaseModel):
    query: str
    search_type: Optional[str] = Field(default="Top", description="Type of search to perform (e.g., 'Top', 'Latest')")
    
class TweetMedia(BaseModel):
    photo: Optional[List[Dict[str, str]]] = None
    video: Optional[List[Dict[str, Dict[str, Any]]]] = None

class Tweet(BaseModel):
    type: str
    tweet_id: str
    screen_name: str
    bookmarks: int
    favorites: int
    created_at: str
    text: str
    lang: str
    quotes: int
    replies: int
    retweets: int
    media: Optional[TweetMedia] = None
    
class SearchTweetsData(BaseModel):
    timeline: List[Tweet]
    next_cursor: Optional[str] = None
    
class SearchTweetsResponse(BaseModel):
    success: bool
    message: str
    data: SearchTweetsData
    
class GetTweetThreadParams(BaseModel):
    id: str = Field(..., description="Tweet ID to retrieve the thread for")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")

class ThreadReply(BaseModel):
    id: str = Field(None, description="Tweet ID")
    likes: int = Field(0, description="Number of likes")
    created_at: str = Field(None, description="Tweet creation timestamp")
    text: str = Field(None, description="Tweet text content")
    display_text: Optional[str] = Field(None, description="Displayed text")
    status: Optional[str] = Field(None, description="Tweet status")
    retweets: int = Field(0, description="Number of retweets")
    bookmarks: int = Field(0, description="Number of bookmarks")
    quotes: int = Field(0, description="Number of quote tweets")
    replies: int = Field(0, description="Number of replies")
    views: Optional[str] = Field(None, description="Number of views")
    lang: str = Field(None, description="Tweet language code")
    conversation_id: str = Field(None, description="Conversation ID")
    author: Optional[TweetAuthor] = Field(None, description="Tweet author information")
    media: Optional[TweetMedia] = Field(None, description="Media content in the tweet")

class TweetThreadData(BaseModel):
    id: str = Field(None, description="Main tweet ID")
    likes: int = Field(0, description="Number of likes")
    created_at: str = Field(None, description="Tweet creation timestamp")
    text: str = Field(None, description="Tweet text content")
    display_text: Optional[str] = Field(None, description="Displayed text")
    status: Optional[str] = Field(None, description="Tweet status")
    retweets: int = Field(0, description="Number of retweets")
    bookmarks: int = Field(0, description="Number of bookmarks")
    quotes: int = Field(0, description="Number of quote tweets")
    replies: int = Field(0, description="Number of replies")
    views: Optional[str] = Field(None, description="Number of views")
    lang: str = Field(None, description="Tweet language code")
    conversation_id: str = Field(None, description="Conversation ID")
    source: Optional[str] = Field(None, description="Source of the tweet")
    author: Optional[TweetAuthor] = Field(None, description="Tweet author information")
    media: Optional[TweetMedia] = Field(None, description="Media content in the tweet")
    thread: List[ThreadReply] = Field([], description="Replies in the thread")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")

class TweetThreadResponse(BaseModel):
    success: bool = True
    message: str = None
    data: TweetThreadData 

class GetLatestRepliesParams(BaseModel):
    id: str = Field(..., description="Tweet ID to get replies for")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")

class ReplyTweet(BaseModel):
    type: str = Field(None, description="Type of tweet")
    tweet_id: str = Field(None, description="Tweet ID")
    screen_name: str = Field(None, description="Author's screen name")
    bookmarks: int = Field(0, description="Number of bookmarks")
    favorites: int = Field(0, description="Number of favorites/likes")
    created_at: str = Field(None, description="Creation timestamp")
    text: str = Field(None, description="Tweet text")
    lang: str = Field(None, description="Tweet language")
    source: Optional[str] = Field(None, description="Source of the tweet")
    quotes: int = Field(0, description="Number of quotes")
    replies: int = Field(0, description="Number of replies")
    conversation_id: str = Field(None, description="Conversation ID")
    retweets: int = Field(0, description="Number of retweets")
    views: Optional[str] = Field(None, description="Number of views")
    entities: Optional[Dict[str, Any]] = Field(None, description="Tweet entities")
    user_info: Optional[Dict[str, Any]] = Field(None, description="User information")
    media: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(None, description="Media attached to the tweet")

class LatestRepliesData(BaseModel):
    status: str = Field(None, description="Status of the request")
    timeline: List[ReplyTweet] = Field([], description="List of reply tweets")
    next_cursor: Optional[str] = Field(None, description="Cursor for the next page")
    prev_cursor: Optional[str] = Field(None, description="Cursor for the previous page")

class LatestRepliesResponse(BaseModel):
    success: bool = True
    message: str = None
    data: LatestRepliesData

class GetListTimelineParams(BaseModel):
    list_id: str
    cursor: Optional[str] = None
    limit: Optional[int] = None
    
    
class GetCommunityTimelineParams(BaseModel):
    community_id: str
    ranking: Optional[str] = None
    cursor: Optional[str] = None
    limit: Optional[int] = None


class GetListFollowersParams(BaseModel):
    list_id: str
    cursor: Optional[str] = None
    limit: Optional[int] = None


class GetListMembersParams(BaseModel):
    list_id: str
    cursor: Optional[str] = None
    limit: Optional[int] = None


class GetSpaceParams(BaseModel):
    id: str
    
    
# Response Schemas
class ListTimelineData(BaseModel):
    timeline: List[Dict[str, Any]]
    next_cursor: Optional[str] = None
    
    
class ListTimelineResponse(BaseModel):
    data: ListTimelineData
    

class CommunityTimelineData(BaseModel):
    timeline: List[Dict[str, Any]]
    next_cursor: Optional[str] = None
    
    
class CommunityTimelineResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: CommunityTimelineData
    
    
class ListFollowerData(BaseModel):
    user_id: str
    screen_name: str
    name: str
    profile_image: str
    description: Optional[str] = None
    followers_count: int
    friends_count: int
    statuses_count: int
    media_count: int
    created_at: str
    location: Optional[str] = None
    blue_verified: bool
    verified: bool
    website: Optional[str] = None
    affiliates: List[Any] = []
    business_account: Optional[Any] = None


class ListFollowersData(BaseModel):
    followers: List[ListFollowerData]
    next_cursor: Optional[str] = None
    
    
class ListFollowersResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: ListFollowersData
    
    
class ListMemberData(BaseModel):
    user_id: str
    screen_name: str
    name: str
    profile_image: str
    description: Optional[str] = None
    followers_count: int
    friends_count: int
    statuses_count: int
    media_count: int
    created_at: str
    location: Optional[str] = None
    blue_verified: bool
    verified: bool
    website: Optional[str] = None
    affiliates: List[Any] = []
    business_account: Optional[Any] = None


class ListMembersData(BaseModel):
    members: List[ListMemberData]
    next_cursor: Optional[str] = None
    
    
class ListMembersResponse(BaseModel):
    success: Optional[bool] = True
    message: Optional[str] = None
    data: ListMembersData
    
    
class SpaceParticipant(BaseModel):
    avatar: str
    display_name: str
    is_verified: bool
    is_blue_verified: bool
    periscope_user_id: str
    screenname: str
    rest_id: str


class SpaceParticipants(BaseModel):
    admins: List[SpaceParticipant]
    speakers: List[SpaceParticipant]


class SpaceData(BaseModel):
    state: str
    id: str
    ended: Optional[str] = None
    started: Optional[int] = None
    locked: bool
    replay_start_time: int
    total_live_listeners: int
    total_replay_watched: int
    content_type: str
    is_space_available_for_replay: bool
    media_key: str
    replay_available: bool
    participants: SpaceParticipants


class SpaceResponse(BaseModel):
    data: SpaceData



class ApiResponse(BaseModel):

    data: Union[
        # User-related
        UserProfileData,
        UserProfileResponse,
        UserTimelineData,
        UserTimelineResponse,
        UserFollowingData,
        UserFollowingResponse,
        UserFollowersData,
        UserFollowersResponse,
        
        # Tweet-related
        TweetData,
        TweetResponse,
        TweetRetweetsData,
        TweetRetweetsResponse,
        TweetThreadData,
        TweetThreadResponse,
        LatestRepliesData,
        LatestRepliesResponse,

        # List & community
        ListTimelineData,
        ListTimelineResponse,
        ListFollowersData,
        ListFollowersResponse,
        ListMembersData,
        ListMembersResponse,

        # Spaces
        SpaceData,
        SpaceResponse
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )
