from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class GetMeParams(BaseModel):
    pass

class GetProfileParams(BaseModel):
    username: Optional[str] = Field(
        None,
        description="LinkedIn username to get profile information for. If not provided, will use the authenticated username."
    )

class SearchPeopleParams(BaseModel):
    keywords: Optional[str] = Field(
        None,
        description="Keywords to search for"
    )
    start: Optional[str] = Field(
        "0",
        description="Pagination start index (0, 10, 20, etc.) as a string"
    )
    geo: Optional[str] = Field(
        None,
        description="Location IDs, comma separated (e.g., 103644278,101165590)"
    )
    schoolId: Optional[str] = Field(
        None,
        description="Filter by school ID"
    )
    firstName: Optional[str] = Field(
        None,
        description="Filter by first name"
    )
    lastName: Optional[str] = Field(
        None,
        description="Filter by last name"
    )
    keywordSchool: Optional[str] = Field(
        None,
        description="Filter by school keyword"
    )
    keywordTitle: Optional[str] = Field(
        None,
        description="Filter by job title keyword"
    )
    company: Optional[str] = Field(
        None,
        description="Filter by company name"
    )

class GetProfilePostsParams(BaseModel):
    username: Optional[str] = Field(
        None,
        description="LinkedIn username to get posts for. If not provided, will use the authenticated username."
    )
    start: Optional[str] = Field(
        None,
        description="Pagination start index (0, 50, 100, etc.) for posts"
    )
    paginationToken: Optional[str] = Field(
        None,
        description="Token from previous call for fetching next page"
    )
    postedAt: Optional[str] = Field(
        None,
        description="Filter posts newer than this date (YYYY-MM-DD HH:MM)"
    )

class GetConnectionCountParams(BaseModel):
    username: Optional[str] = Field(None, description="LinkedIn username. If not provided, will use the authenticated username.")

class GetDataConnectionCountParams(BaseModel):
    username: Optional[str] = Field(None, description="LinkedIn username. If not provided, will use the authenticated username.")

class SortOption(str, Enum):
    mostRelevant = "mostRelevant"
    mostRecent = "mostRecent"

class GetPostCommentsParams(BaseModel):
    urn: str = Field(..., description="Post (activity) urn value")
    sort: SortOption = Field(SortOption.mostRelevant, description="Sort order for comments")
    page: Optional[str] = Field(None, description="Page number for pagination")
    paginationToken: Optional[str] = Field(
        None, 
        description="Token from previous call for fetching next page"
    )

    @validator('page', pre=True, always=True)
    def validate_page(cls, v):
        if v is not None and not isinstance(v, str):
            return str(v)
        return v

class PostCommentAuthor(BaseModel):
    author_data: Optional[Dict[str, Any]] = None

class PostComment(BaseModel):
    isPinned: Optional[bool] = None
    isEdited: Optional[bool] = None
    threadUrn: Optional[str] = None
    createdAt: Optional[int] = None
    createdAtString: Optional[str] = None
    permalink: Optional[str] = None
    text: Optional[str] = None
    author: Optional[PostCommentAuthor] = None

class GetPostCommentsResult(BaseModel):
    items: List[PostComment]
    total: Optional[int] = None
    totalPage: Optional[int] = None
    paginationToken: Optional[str] = None

class ProfilePosition(BaseModel):
    companyId: Optional[int] = None
    companyName: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start: Optional[Dict[str, Any]] = None
    end: Optional[Dict[str, Any]] = None

class ProfileEducation(BaseModel):
    schoolName: Optional[str] = None
    fieldOfStudy: Optional[str] = None
    degree: Optional[str] = None
    start: Optional[Dict[str, Any]] = None
    end: Optional[Dict[str, Any]] = None

class ProfileSkill(BaseModel):
    name: Optional[str] = None

class Geo(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    full: Optional[str] = None

class ProfileImageItem(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None

class Profile(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    profilePicture: Optional[str] = None
    backgroundImage: Optional[List[ProfileImageItem]] = None
    isPremium: Optional[bool] = None
    isTopVoice: Optional[bool] = None
    isCreator: Optional[bool] = None
    geo: Optional[Geo] = None
    position: Optional[List[ProfilePosition]] = None
    educations: Optional[List[ProfileEducation]] = None
    skills: Optional[List[ProfileSkill]] = None

class SearchPersonResult(BaseModel):
    fullName: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    profilePicture: Optional[str] = None
    location: Optional[str] = None
    profileURL: Optional[str] = None
    username: Optional[str] = None

class ProfilePost(BaseModel):
    post_data: Dict[str, Any]

class SearchPeopleResults(BaseModel):
    total: int
    items: List[SearchPersonResult]

class GetProfilePostsResult(BaseModel):
    items: List[ProfilePost]
    paginationToken: Optional[str] = None

class ProfileList(BaseModel):
    profiles: List[Profile]

class ProfileResponse(BaseModel):
    data: Profile

class ProfileListResponse(BaseModel):
    data: ProfileList

class SearchPeopleResponse(BaseModel):
    data: SearchPeopleResults

class GetProfilePostsResponse(BaseModel):
    data: GetProfilePostsResult

class ConnectionCount(BaseModel):
    connection: Optional[int] = None
    follower: Optional[int] = None

class Language(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None

class Course(BaseModel):
    name: Optional[str] = None
    number: Optional[str] = None

class DataConnectionCountData(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    isOpenToWork: Optional[bool] = None
    isHiring: Optional[bool] = None
    profilePicture: Optional[str] = None
    summary: Optional[str] = None
    headline: Optional[str] = None
    geo: Optional[Geo] = None
    languages: Optional[List[Language]] = None
    educations: Optional[List[ProfileEducation]] = None
    position: Optional[List[ProfilePosition]] = None
    skills: Optional[List[ProfileSkill]] = None
    courses: Optional[List[Course]] = None

class DataConnectionCount(BaseModel):
    connection: Optional[int] = None
    data: Optional[DataConnectionCountData] = None
    follower: Optional[int] = None

class GetPostCommentsResponse(BaseModel):
    data: GetPostCommentsResult
    component: Optional[Dict[str, Any]] = None

class SimilarProfilesParams(BaseModel):
    url: str = Field(..., description="URL of the LinkedIn profile to find similar profiles for")

class ProfilePicture(BaseModel):
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class SimilarProfileItem(BaseModel):
    id: Optional[int] = None
    urn: Optional[str] = None
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    profilePictures: Optional[List[ProfilePicture]] = Field(None, alias='profilePictures')
    headline: Optional[str] = None
    geo: Optional[Dict[str, Any]] = None
    projects: Optional[Dict[str, Any]] = None

class SimilarProfilesData(BaseModel):
    items: Optional[List[SimilarProfileItem]] = None

    @validator('items', pre=True, always=True)
    def set_items_to_empty_list_if_none(cls, v):
        if v is None:
            return []
        return v

class SimilarProfilesResponse(BaseModel):
    success: bool
    message: str
    data: SimilarProfilesData

class GetCompanyDetailsParams(BaseModel):
    username: Optional[str] = Field(None, description="The company's LinkedIn page username (e.g., 'google'). If not provided, will use the authenticated username.")

class CompanyHeadquarter(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    line1: Optional[str] = None

class CompanyDetails(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    universalName: Optional[str] = None
    linkedinUrl: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    logoUrl: Optional[str] = None
    staffCount: Optional[int] = None
    headquarter: Optional[CompanyHeadquarter] = None
    industries: Optional[List[str]] = None
    specialities: Optional[List[str]] = None
    website: Optional[str] = None
    followerCount: Optional[int] = None
    staffCountRange: Optional[str] = None
    fundingType: Optional[str] = None   

class CompanyDetailsApiResponse(BaseModel):
    success: bool
    message: str
    data: CompanyDetails

class CompanyDetailsResponse(BaseModel):
    data: CompanyDetails
    component: Optional[Dict[str, Any]] = None

class SearchCompaniesParams(BaseModel):
    keyword: Optional[str] = Field(None, description="Keyword to search for companies")
    locations: Optional[List[int]] = Field(None, description="List of location IDs")
    companySizes: Optional[List[str]] = Field(None, description="List of company size codes (e.g., D, E, F, G)")
    hasJobs: Optional[bool] = Field(None, description="Filter by companies that have job openings")
    industries: Optional[List[int]] = Field(None, description="List of industry codes")
    page: Optional[int] = Field(1, ge=1, description="Page number for results")

class SearchCompaniesData(BaseModel):
    items: List[Dict[str, Any]]
    total: Optional[int] = None
    totalPages: Optional[int] = None
    currentPage: Optional[int] = None

class SearchCompaniesResponse(BaseModel):
    success: bool
    message: str
    data: SearchCompaniesData

class SearchCompaniesEndpointResponse(BaseModel):
    data: SearchCompaniesData
    component: Optional[Dict[str, Any]] = None

class ConnectionCountResponse(BaseModel):
    data: ConnectionCount

class DataConnectionCountResponse(BaseModel):
    data: DataConnectionCount

class CompanyJobsSortOption(str, Enum):
    mostRecent = "mostRecent"
    mostRelevant = "mostRelevant"

class CompanyJobsParams(BaseModel):
    companyIds: List[int] = Field(..., description="List of company IDs to fetch jobs for")
    page: Optional[int] = Field(1, ge=1, description="Page number for results")
    sort: Optional[CompanyJobsSortOption] = Field(CompanyJobsSortOption.mostRecent, description="Sorting criteria for jobs")

class CompanyJobItem(BaseModel):
    job_details: Dict[str, Any]

class CompanyJobsData(BaseModel):
    items: Optional[List[Dict[str, Any]]] = None
    total: Optional[int] = None

class CompanyJobsResponse(BaseModel):
    success: bool
    message: str
    data: CompanyJobsData

class CompanyJobsEndpointResponse(BaseModel):
    data: CompanyJobsData
    component: Optional[Dict[str, Any]] = None



class GetCompanyPostsParams(BaseModel):
    username: str = Field(..., description="Company username (e.g., 'google')")
    start: Optional[str] = Field("0", description="Pagination start index (0, 50, 100, etc.)")
    paginationToken: Optional[str] = Field(None, description="Token from previous call for next page")

class CompanyPostItem(BaseModel):
    post_details: Dict[str, Any]

class CompanyPostsList(BaseModel):
    posts: List[Dict[str, Any]]

class GetCompanyPostsApiResponse(BaseModel):
    success: bool
    message: str
    data: List[Dict[str, Any]]

class GetCompanyPostsEndpointResponse(BaseModel):
    data: CompanyPostsList
    component: Optional[Dict[str, Any]] = None



class GetCompanyPostCommentsParams(BaseModel):
    urn: str = Field(..., description="Company post URN value")
    sort: SortOption = Field(SortOption.mostRelevant, description="Sort order for comments")
    page: Optional[str] = Field("1", description="Page number for pagination")

    @validator('page', pre=True, always=True)
    def validate_page(cls, v):
        if v is not None and not isinstance(v, str):
            return str(v)
        return v

class CompanyPostCommentItem(BaseModel):
    comment_details: Dict[str, Any]

class CompanyPostCommentsList(BaseModel):
    comments: List[Dict[str, Any]]

class GetCompanyPostCommentsApiResponse(BaseModel):
    success: bool
    message: str
    data: List[Dict[str, Any]]

class GetCompanyPostCommentsEndpointResponse(BaseModel):
    data: CompanyPostCommentsList
    component: Optional[Dict[str, Any]] = None

class SearchPostsSortBy(str, Enum):
    date_posted = "date_posted"

class SearchPostsParams(BaseModel):
    keyword: Optional[str] = Field(None, description="Keyword to search in posts")
    sortBy: Optional[SearchPostsSortBy] = Field(None, description="Sort order for posts")
    datePosted: Optional[str] = Field(None, description="Filter by date posted (e.g., last_24_hours, last_week)")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    contentType: Optional[str] = Field(None, description="Filter by content type (e.g., ARTICLE, VIDEO, IMAGE)")
    fromMember: Optional[List[str]] = Field(None, description="List of member profile URNs to filter posts from")
    fromCompany: Optional[List[int]] = Field(None, description="List of company IDs to filter posts from")
    mentionsMember: Optional[List[str]] = Field(None, description="List of member profile URNs mentioned in posts")
    mentionsOrganization: Optional[List[int]] = Field(None, description="List of company IDs mentioned in posts")
    authorIndustry: Optional[List[int]] = Field(None, description="List of author industry codes")
    authorCompany: Optional[List[int]] = Field(None, description="List of author company IDs")
    authorTitle: Optional[str] = Field(None, description="Filter by author job title keyword")

class SearchPostsAuthor(BaseModel):
    fullName: Optional[str] = None
    headline: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    profilePictures: Optional[List[ProfilePicture]] = None # Reusing ProfilePicture
    type: Optional[str] = None

class SearchPostsSocialActivity(BaseModel):
    numComments: Optional[int] = None
    likeCount: Optional[int] = None
    appreciationCount: Optional[int] = None
    empathyCount: Optional[int] = None
    InterestCount: Optional[int] = None # Note: Case might be different in actual API
    praiseCount: Optional[int] = None
    funnyCount: Optional[int] = None
    maybeCount: Optional[int] = None
    totalReactionCount: Optional[int] = None

class SearchPostsItem(BaseModel):
    urn: Optional[str] = None
    url: Optional[str] = None
    template: Optional[str] = None
    text: Optional[str] = None
    postedAt: Optional[str] = None
    postedDate: Optional[str] = None
    postedDateTimestamp: Optional[int] = None
    reposted: Optional[bool] = None
    resharedPost: Optional[Dict[str, Any]] = None # Structure unknown
    video: Optional[Dict[str, Any]] = None # Structure mostly null/unknown
    entity: Optional[Dict[str, Any]] = None # Structure unknown
    article: Optional[Dict[str, Any]] = None # Structure unknown
    object: Optional[Dict[str, Any]] = None # Structure unknown
    author: Optional[SearchPostsAuthor] = None
    socialActivityCountsInsight: Optional[SearchPostsSocialActivity] = None

class SearchPostsData(BaseModel):
    total: Optional[int] = None
    count: Optional[int] = None
    items: Optional[List[SearchPostsItem]] = None # Items can be null/missing

    @validator('items', pre=True, always=True)
    def set_items_to_empty_list_if_none(cls, v):
        if v is None:
            return []
        return v

class SearchPostsResponse(BaseModel): # Raw API Response
    success: bool
    message: Optional[str] = None
    data: Optional[SearchPostsData] = None

class SearchPostsEndpointResponse(BaseModel):
    data: Optional[SearchPostsData] = None
    component: Optional[Dict[str, Any]] = None


class GetPostParams(BaseModel):
    url: str = Field(..., description="URL of the LinkedIn post")

class GetPostAuthor(BaseModel):
    id: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    headline: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    profilePictures: Optional[List[ProfilePicture]] = None
    urn: Optional[str] = None

class GetPostArticle(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    link: Optional[str] = None
    newsletter: Optional[Dict[str, Any]] = None

class GetPostData(BaseModel):
    isBrandPartnership: Optional[bool] = None
    text: Optional[str] = None
    totalReactionCount: Optional[int] = None
    likeCount: Optional[int] = None
    appreciationCount: Optional[int] = None
    empathyCount: Optional[int] = None
    praiseCount: Optional[int] = None
    commentsCount: Optional[int] = None
    repostsCount: Optional[int] = None
    shareUrl: Optional[str] = None
    postedAt: Optional[str] = None
    postedDate: Optional[str] = None
    postedDateTimestamp: Optional[int] = None
    urn: Optional[str] = None
    shareUrn: Optional[str] = None
    author: Optional[GetPostAuthor] = None
    company: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    celebration: Optional[Dict[str, Any]] = None
    poll: Optional[Dict[str, Any]] = None
    article: Optional[GetPostArticle] = None
    entity: Optional[Dict[str, Any]] = None

class GetPostResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[GetPostData] = None

class GetPostEndpointResponse(BaseModel):
    data: Optional[GetPostData] = None
    component: Optional[Dict[str, Any]] = None

class GetJobDetailsParams(BaseModel):
    id: str = Field(..., description="LinkedIn job listing ID")

class JobApplyMethod(BaseModel):
    companyApplyUrl: Optional[str] = None
    easyApplyUrl: Optional[str] = None

class JobCompanyHeadquarter(BaseModel):
    geographicArea: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    line2: Optional[str] = None
    line1: Optional[str] = None

class JobCompanyStaffCountRange(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None

class JobCompany(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    universalName: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    url: Optional[str] = None
    followerCount: Optional[int] = None
    staffCount: Optional[int] = None
    staffCountRange: Optional[JobCompanyStaffCountRange] = None
    specialities: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    headquarter: Optional[JobCompanyHeadquarter] = None

class JobContentLanguage(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None

class JobDetails(BaseModel):
    id: Optional[str] = None
    state: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    applyMethod: Optional[JobApplyMethod] = None
    company: Optional[JobCompany] = None
    contentLanguage: Optional[JobContentLanguage] = None
    location: Optional[str] = None
    type: Optional[str] = None
    applies: Optional[int] = None
    views: Optional[int] = None
    workRemoteAllowed: Optional[bool] = None
    workPlace: Optional[str] = None
    expireAt: Optional[int] = None
    formattedJobFunctions: Optional[List[str]] = None
    jobFunctions: Optional[List[str]] = None
    industries: Optional[List[int]] = None
    formattedIndustries: Optional[List[str]] = None
    formattedExperienceLevel: Optional[str] = None
    listedAt: Optional[int] = None
    listedAtDate: Optional[str] = None
    originalListedAt: Optional[int] = None
    originalListedDate: Optional[str] = None

class GetJobDetailsData(BaseModel):
    success: bool
    message: str
    data: JobDetails

class GetJobDetailsResponse(BaseModel):
    data: JobDetails
    component: Optional[Dict[str, Any]] = None

class SearchJobsParams(BaseModel):
    keywords: str = Field(..., description="Keywords to search for jobs")
    locationId: Optional[str] = Field(None, description="Location ID for job search")
    datePosted: Optional[str] = Field(None, description="Filter by date posted (anyTime, pastMonth, pastWeek, past24Hours)")
    salary: Optional[str] = Field(None, description="Salary filter (e.g., 40k+, 60k+, 80k+, etc.)")
    jobType: Optional[str] = Field(None, description="Job type (fullTime, partTime, contract, internship)")
    experienceLevel: Optional[str] = Field(None, description="Experience level (internship, associate, director, entryLevel, midSeniorLevel, executive)")
    titleIds: Optional[str] = Field(None, description="Comma-separated title IDs")
    functionIds: Optional[str] = Field(None, description="Comma-separated function IDs")
    start: Optional[str] = Field("0", description="Start index for pagination (0, 25, 50, etc.)")
    industryIds: Optional[str] = Field(None, description="Comma-separated industry IDs")
    onsiteRemote: Optional[str] = Field(None, description="Work setting (onSite, remote, hybrid)")
    sort: Optional[str] = Field("mostRelevant", description="Sort option (mostRelevant, mostRecent)")
    companyIds: Optional[str] = Field(None, description="Comma-separated company IDs")

class JobSearchItem(BaseModel):
    id: str
    title: str
    url: str
    referenceId: Optional[str] = None
    posterId: Optional[str] = None
    company: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    type: Optional[str] = None
    postDate: Optional[str] = None
    benefits: Optional[str] = None

class JobSearchData(BaseModel):
    items: List[JobSearchItem]
    total: Optional[int] = None

class JobSearchResponse(BaseModel):
    success: bool
    message: str
    data: List[JobSearchItem]
    total: Optional[int] = None

class JobSearchList(BaseModel):
    jobs: List[JobSearchItem]
    total: Optional[int] = None

class JobSearchEndpointResponse(BaseModel):
    data: JobSearchList
    component: Optional[Dict[str, Any]] = None

class SearchLocationsParams(BaseModel):
    keyword: str = Field(..., description="Location keyword to search for (e.g., 'berlin', 'new york')")

class LocationItem(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

class LocationsData(BaseModel):
    items: List[LocationItem]

class SearchLocationsResponse(BaseModel):
    success: bool
    message: str
    data: LocationsData

class LocationsList(BaseModel):
    locations: List[LocationItem]

class SearchLocationsEndpointResponse(BaseModel):
    data: LocationsList
    component: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    data: Union[
        Profile, 
        ProfileList, 
        SearchPeopleResults, 
        GetProfilePostsResult, 
        ConnectionCount, 
        DataConnectionCount,
        GetPostCommentsResult,
        SimilarProfilesResponse,
        CompanyDetails,
        SearchCompaniesData,
        CompanyJobsData,
        CompanyPostsList,
        CompanyPostCommentsList,
        SearchPostsData,
        GetPostData,
        JobDetails,
        JobSearchList,
        LocationsList
    ]
    component: Optional[Dict[str, Any]] = None