from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class GetProfileParams(BaseModel):
    username: str = Field(..., description="LinkedIn username or profile ID")


class SearchPeopleParams(BaseModel):
    keywords: str = Field(..., description="Search keywords")
    start: Optional[int] = Field(0, description="Starting position for pagination")
    geo: Optional[str] = Field(None, description="Geographic location IDs, comma separated")


class GetProfilePostsParams(BaseModel):
    username: str = Field(..., description="LinkedIn username")
    pagination_token: Optional[str] = Field(None, description="Pagination token for next page of results")


class DateInfo(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


class Image(BaseModel):
    url: str
    width: Optional[int] = None
    height: Optional[int] = None


class Geo(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    full: Optional[str] = None
    countryCode: Optional[str] = None


class Education(BaseModel):
    start: Optional[DateInfo] = None
    end: Optional[DateInfo] = None
    fieldOfStudy: Optional[str] = None
    degree: Optional[str] = None
    grade: Optional[str] = None
    schoolName: Optional[str] = None
    description: Optional[str] = None
    activities: Optional[str] = None
    url: Optional[str] = None
    schoolId: Optional[str] = None
    logo: Optional[List[Image]] = None


class MultiLocale(BaseModel):
    en_US: Optional[str] = None
    en: Optional[str] = None


class Position(BaseModel):
    companyId: Optional[int] = None
    companyName: Optional[str] = None
    companyUsername: Optional[str] = None
    companyURL: Optional[str] = None
    companyLogo: Optional[str] = None
    companyIndustry: Optional[str] = None
    companyStaffCountRange: Optional[str] = None
    title: Optional[str] = None
    multiLocaleTitle: Optional[MultiLocale] = None
    multiLocaleCompanyName: Optional[MultiLocale] = None
    location: Optional[str] = None
    description: Optional[str] = None
    employmentType: Optional[str] = None
    start: Optional[DateInfo] = None
    end: Optional[DateInfo] = None


class Skill(BaseModel):
    name: Optional[str] = None
    passedSkillAssessment: Optional[bool] = None
    endorsementsCount: Optional[int] = None


class SupportedLocale(BaseModel):
    country: Optional[str] = None
    language: Optional[str] = None


class ProfileData(BaseModel):
    id: Optional[int] = None
    urn: Optional[str] = None
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    isTopVoice: Optional[bool] = None
    isCreator: Optional[bool] = None
    isPremium: Optional[bool] = None
    profilePicture: Optional[str] = None
    backgroundImage: Optional[List[Image]] = None
    summary: Optional[str] = None
    headline: Optional[str] = None
    geo: Optional[Geo] = None
    educations: Optional[List[Education]] = None
    position: Optional[List[Position]] = None
    fullPositions: Optional[List[Position]] = None
    skills: Optional[List[Skill]] = None
    projects: Optional[Dict[str, Any]] = None
    supportedLocales: Optional[List[SupportedLocale]] = None
    multiLocaleFirstName: Optional[MultiLocale] = None
    multiLocaleLastName: Optional[MultiLocale] = None
    multiLocaleHeadline: Optional[MultiLocale] = None


class PersonSearchItem(BaseModel):
    fullName: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    profilePicture: Optional[str] = None
    location: Optional[str] = None
    profileURL: Optional[str] = None
    username: Optional[str] = None


class SearchPeopleData(BaseModel):
    total: Optional[int] = None
    items: List[PersonSearchItem] = []


class SearchPeopleResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[SearchPeopleData] = None


class ProfilePicture(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None


class Author(BaseModel):
    id: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    headline: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    profilePictures: Optional[List[ProfilePicture]] = None
    urn: Optional[str] = None


class Video(BaseModel):
    url: Optional[str] = None
    poster: Optional[str] = None
    duration: Optional[int] = None
    thumbnails: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None


class Post(BaseModel):
    isBrandPartnership: Optional[bool] = None
    text: Optional[str] = None
    totalReactionCount: Optional[int] = None
    likeCount: Optional[int] = None
    repostsCount: Optional[int] = None
    commentsCount: Optional[int] = None
    postUrl: Optional[str] = None
    shareUrl: Optional[str] = None
    postedAt: Optional[str] = None
    postedDate: Optional[str] = None
    postedDateTimestamp: Optional[int] = None
    urn: Optional[str] = None
    author: Optional[Author] = None
    video: Optional[List[Video]] = None
    company: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    celebration: Optional[Dict[str, Any]] = None
    poll: Optional[Dict[str, Any]] = None
    article: Optional[Dict[str, Any]] = None
    entity: Optional[Dict[str, Any]] = None


class ProfilePostsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: List[Post] = []
    paginationToken: Optional[str] = None


class GetProfilePostCommentsParams(BaseModel):
    urn: str = Field(..., description="LinkedIn post URN")
    sort: Optional[str] = Field("mostRelevant", description="Sort order for comments (mostRelevant, latest)")
    page: Optional[int] = Field(1, description="Page number for pagination")


class Comment(BaseModel):
    isPinned: Optional[bool] = None
    isEdited: Optional[bool] = None
    threadUrn: Optional[str] = None
    createdAt: Optional[int] = None
    createdAtString: Optional[str] = None
    permalink: Optional[str] = None
    text: Optional[str] = None
    author: Optional[Dict[str, Any]] = None


class ProfilePostCommentsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: List[Comment] = []
    total: Optional[int] = None
    totalPage: Optional[int] = None
    paginationToken: Optional[str] = None


class GetConnectionCountParams(BaseModel):
    username: str = Field(..., description="LinkedIn username")


class Language(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None


class Course(BaseModel):
    name: Optional[str] = None
    number: Optional[str] = None


class ConnectionData(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    isOpenToWork: Optional[bool] = None
    isHiring: Optional[bool] = None
    profilePicture: Optional[str] = None
    summary: Optional[str] = None
    headline: Optional[str] = None
    geo: Optional[Geo] = None
    languages: Optional[List[Language]] = None
    educations: Optional[List[Education]] = None
    position: Optional[List[Position]] = None
    skills: Optional[List[Skill]] = None
    courses: Optional[List[Course]] = None


class ConnectionCountResponse(BaseModel):
    connection: Optional[int] = None
    data: Optional[ConnectionData] = None
    follower: Optional[int] = None


class GetDataConnectionCountParams(BaseModel):
    username: str = Field(..., description="LinkedIn username")


class GetCompanyDetailsParams(BaseModel):
    username: str = Field(..., description="LinkedIn company username")


class HeadquarterInfo(BaseModel):
    geographicArea: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    line1: Optional[str] = None


class CompanyImages(BaseModel):
    logo: Optional[str] = None
    cover: Optional[str] = None


class CallToActionMessage(BaseModel):
    textDirection: Optional[str] = None
    text: Optional[str] = None


class CallToAction(BaseModel):
    callToActionType: Optional[str] = None
    visible: Optional[bool] = None
    callToActionMessage: Optional[CallToActionMessage] = None
    url: Optional[str] = None


class MoneyRaised(BaseModel):
    currencyCode: Optional[str] = None
    amount: Optional[str] = None


class AnnouncedOn(BaseModel):
    month: Optional[int] = None
    day: Optional[int] = None
    year: Optional[int] = None


class LeadInvestor(BaseModel):
    name: Optional[str] = None
    investorCrunchbaseUrl: Optional[str] = None


class LastFundingRound(BaseModel):
    investorsCrunchbaseUrl: Optional[str] = None
    leadInvestors: Optional[List[LeadInvestor]] = None
    fundingRoundCrunchbaseUrl: Optional[str] = None
    fundingType: Optional[str] = None
    moneyRaised: Optional[MoneyRaised] = None
    numOtherInvestors: Optional[int] = None
    announcedOn: Optional[AnnouncedOn] = None


class FundingData(BaseModel):
    updatedAt: Optional[str] = None
    updatedDate: Optional[str] = None
    numFundingRounds: Optional[int] = None
    lastFundingRound: Optional[LastFundingRound] = None


class CompanyDetailsData(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    universalName: Optional[str] = None
    linkedinUrl: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    phone: Optional[str] = None
    Images: Optional[CompanyImages] = None
    isClaimable: Optional[bool] = None
    backgroundCoverImages: Optional[List[Image]] = None
    logos: Optional[List[Image]] = None
    staffCount: Optional[int] = None
    headquarter: Optional[HeadquarterInfo] = None
    locations: Optional[List[Dict[str, Any]]] = None
    industries: Optional[List[str]] = None
    specialities: Optional[List[str]] = None
    website: Optional[str] = None
    founded: Optional[Any] = None
    callToAction: Optional[CallToAction] = None
    followerCount: Optional[int] = None
    staffCountRange: Optional[str] = None
    crunchbaseUrl: Optional[str] = None
    fundingData: Optional[FundingData] = None


class CompanyDetailsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[CompanyDetailsData] = None


class SearchCompaniesParams(BaseModel):
    keyword: Optional[str] = Field("", description="Search keyword")
    locations: Optional[List[int]] = Field(None, description="Location IDs")
    companySizes: Optional[List[str]] = Field(None, description="Company sizes (e.g. 'D', 'E', 'F', 'G')")
    hasJobs: Optional[bool] = Field(None, description="Filter for companies with job listings")
    industries: Optional[List[int]] = Field(None, description="Industry IDs")
    page: Optional[int] = Field(1, description="Page number for pagination")


class SearchCompaniesData(BaseModel):
    items: Optional[List[Dict[str, Any]]] = []
    total: Optional[int] = None
    totalPages: Optional[int] = None
    currentPage: Optional[int] = None


class SearchCompaniesResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[SearchCompaniesData] = None


class CompanyJobsParams(BaseModel):
    companyIds: List[int] = Field(..., description="List of company IDs")
    page: Optional[int] = Field(1, description="Page number for pagination")
    sort: Optional[str] = Field("mostRecent", description="Sort order for jobs (e.g. 'mostRecent')")


class CompanyJobsData(BaseModel):
    items: Optional[List[Dict[str, Any]]] = []
    total: Optional[int] = None


class CompanyJobsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[CompanyJobsData] = None


class GetCompanyPostsParams(BaseModel):
    username: str = Field(..., description="LinkedIn company username")
    start: Optional[int] = Field(0, description="Starting position for pagination")


class CompanyPostsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = []


class GetProfileEmailParams(BaseModel):
    url: str = Field(..., description="LinkedIn profile URL")


class ProfileEmailData(BaseModel):
    emails: Optional[Any] = None
    profileData: Optional[ProfileData] = None


class ProfileEmailResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[ProfileEmailData] = None


class GetCompanyEmployeesCountParams(BaseModel):
    companyId: str = Field(..., description="LinkedIn company ID")
    locations: List[str] = Field(default_factory=list, description="List of location IDs")


class CompanyEmployeesGroupData(BaseModel):
    Current_Function: Optional[List[Dict[str, Any]]] = Field(None, alias="Current Function")
    Field_of_Study: Optional[List[Dict[str, Any]]] = Field(None, alias="Field of Study")
    Locations: Optional[List[Dict[str, Any]]] = None
    School: Optional[List[Dict[str, Any]]] = None
    Service_categories: Optional[List[Dict[str, Any]]] = Field(None, alias="Service categories")
    Skill_Explicit: Optional[List[Dict[str, Any]]] = Field(None, alias="Skill Explicit")


class CompanyEmployeesCountData(BaseModel):
    byGroup: Optional[CompanyEmployeesGroupData] = None
    total: Optional[int] = None


class CompanyEmployeesCountResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[CompanyEmployeesCountData] = None


class SearchJobsParams(BaseModel):
    keywords: str = Field(..., description="Search keywords for jobs")
    locationId: str = Field(..., description="Location ID for job search")
    datePosted: str = Field("anyTime", description="Filter for job posting date (e.g. 'anyTime')")
    sort: str = Field("mostRelevant", description="Sort order for results (e.g. 'mostRelevant')")


class SearchJobsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: List[Dict[str, Any]] = []
    total: Optional[int] = None


class GetJobDetailsParams(BaseModel):
    id: str = Field(..., description="LinkedIn job ID")


class StaffCountRange(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None


class JobCompanyHeadquarter(BaseModel):
    geographicArea: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    line2: Optional[str] = None
    line1: Optional[str] = None


class JobCompany(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    universalName: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    url: Optional[str] = None
    followerCount: Optional[int] = None
    staffCount: Optional[int] = None
    staffCountRange: Optional[StaffCountRange] = None
    specialities: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    headquarter: Optional[JobCompanyHeadquarter] = None


class ApplyMethod(BaseModel):
    companyApplyUrl: Optional[str] = None
    easyApplyUrl: Optional[str] = None


class ContentLanguage(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


class JobDetailsData(BaseModel):
    id: Optional[str] = None
    state: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    applyMethod: Optional[ApplyMethod] = None
    company: Optional[JobCompany] = None
    contentLanguage: Optional[ContentLanguage] = None
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


class JobDetailsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[JobDetailsData] = None


class GetHiringTeamParams(BaseModel):
    id: str = Field(..., description="LinkedIn job ID")
    url: str = Field(..., description="LinkedIn job URL")


class HiringTeamMemberProfilePicture(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None


class HiringTeamMember(BaseModel):
    fullName: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    headline: Optional[str] = None
    profilePicture: Optional[List[HiringTeamMemberProfilePicture]] = None


class HiringTeamData(BaseModel):
    items: List[HiringTeamMember] = []


class HiringTeamResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[HiringTeamData] = None


class SearchPostsParams(BaseModel):
    keyword: Optional[str] = Field("", description="Search keyword")
    sortBy: str = Field("date_posted", description="Sort order for posts")
    datePosted: Optional[str] = Field("", description="Filter by date posted")
    page: Optional[int] = Field(1, description="Page number")
    contentType: Optional[str] = Field("", description="Type of content to filter")
    fromMember: Optional[List[str]] = Field(None, description="Filter by member URNs")
    fromCompany: Optional[List[int]] = Field(None, description="Filter by company IDs")
    mentionsMember: Optional[List[str]] = Field(None, description="Filter by mentioned member URNs")
    mentionsOrganization: Optional[List[int]] = Field(None, description="Filter by mentioned organization IDs")
    authorIndustry: Optional[List[int]] = Field(None, description="Filter by author industry IDs")
    authorCompany: Optional[List[int]] = Field(None, description="Filter by author company IDs")
    authorTitle: Optional[str] = Field("", description="Filter by author title")


class PostAuthorProfilePicture(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None


class PostAuthor(BaseModel):
    fullName: Optional[str] = None
    headline: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    profilePictures: Optional[List[PostAuthorProfilePicture]] = None
    type: Optional[str] = None


class SocialActivityCountsInsight(BaseModel):
    numComments: Optional[int] = None
    likeCount: Optional[int] = None
    appreciationCount: Optional[int] = None
    empathyCount: Optional[int] = None
    InterestCount: Optional[int] = None
    praiseCount: Optional[int] = None
    funnyCount: Optional[int] = None
    maybeCount: Optional[int] = None
    totalReactionCount: Optional[int] = None


class PostVideo(BaseModel):
    thumbnails: Optional[Any] = None
    video: Optional[Any] = None


class Post(BaseModel):
    urn: Optional[str] = None
    url: Optional[str] = None
    template: Optional[str] = None
    text: Optional[str] = None
    postedAt: Optional[str] = None
    postedDate: Optional[str] = None
    postedDateTimestamp: Optional[int] = None
    reposted: Optional[bool] = None
    resharedPost: Optional[Dict[str, Any]] = None
    video: Optional[PostVideo] = None
    entity: Optional[Dict[str, Any]] = None
    article: Optional[Dict[str, Any]] = None
    object: Optional[Dict[str, Any]] = None
    author: Optional[PostAuthor] = None
    socialActivityCountsInsight: Optional[SocialActivityCountsInsight] = None


class SearchPostsData(BaseModel):
    total: Optional[int] = None
    count: Optional[int] = None
    items: List[Post] = []


class SearchPostsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[SearchPostsData] = None


class GetPostParams(BaseModel):
    url: str = Field(..., description="LinkedIn post URL")


class PostArticle(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    link: Optional[str] = None
    newsletter: Optional[Dict[str, Any]] = None


class PostAuthorProfilePicture(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None


class PostAuthor(BaseModel):
    id: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    headline: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    profilePictures: Optional[List[PostAuthorProfilePicture]] = None
    urn: Optional[str] = None


class PostData(BaseModel):
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
    author: Optional[PostAuthor] = None
    company: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    celebration: Optional[Dict[str, Any]] = None
    poll: Optional[Dict[str, Any]] = None
    article: Optional[PostArticle] = None
    entity: Optional[Dict[str, Any]] = None


class GetPostResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[PostData] = None


class GetArticleParams(BaseModel):
    url: str = Field(..., description="LinkedIn article URL")


class ArticleImage(BaseModel):
    url: str
    width: Optional[int] = None
    height: Optional[int] = None


class ArticleSocialActivityCounts(BaseModel):
    numComments: Optional[int] = None
    likeCount: Optional[int] = None
    appreciationCount: Optional[int] = None
    empathyCount: Optional[int] = None
    InterestCount: Optional[int] = None
    praiseCount: Optional[int] = None
    funnyCount: Optional[int] = None
    maybeCount: Optional[int] = None
    totalReactionCount: Optional[int] = None
    numShares: Optional[int] = None


class ArticleData(BaseModel):
    urn: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    images: Optional[List[ArticleImage]] = None
    contentHTML: Optional[str] = None
    publishedAt: Optional[int] = None
    publishedDate: Optional[str] = None
    totalSocialActivityCounts: Optional[ArticleSocialActivityCounts] = None
    permalink: Optional[str] = None
    state: Optional[str] = None
    articleType: Optional[str] = None


class GetArticleResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[ArticleData] = None


class GetArticleCommentsParams(BaseModel):
    url: str = Field(..., description="LinkedIn article URL")
    page: Optional[int] = Field(1, description="Page number for pagination")
    sort: Optional[str] = Field("REVERSE_CHRONOLOGICAL", description="Sort order for comments")


class ArticleCommentAuthorProfile(BaseModel):
    id: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    headline: Optional[str] = None
    profilePicture: Optional[List[ProfilePicture]] = None


class ArticleComment(BaseModel):
    text: Optional[str] = None
    permalink: Optional[str] = None
    authorProfile: Optional[ArticleCommentAuthorProfile] = None
    createdAt: Optional[int] = None
    createdDate: Optional[str] = None
    totalSocialActivityCounts: Optional[Dict[str, Any]] = None


class ArticleCommentsData(BaseModel):
    currentPage: Optional[str] = None
    items: List[ArticleComment] = []
    total: Optional[int] = None
    totalPages: Optional[int] = None


class GetArticleCommentsResponse(BaseModel):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[ArticleCommentsData] = None


class ApiResponse(BaseModel):
    data: Union[
        Dict[str, Any],
        ProfileData,
        SearchPeopleResponse,
        ProfilePostsResponse,
        ProfilePostCommentsResponse,
        ConnectionCountResponse,
        CompanyDetailsResponse,
        SearchCompaniesResponse,
        CompanyJobsResponse,
        CompanyPostsResponse,
        ProfileEmailResponse,
        CompanyEmployeesCountResponse,
        SearchJobsResponse,
        JobDetailsResponse,
        HiringTeamResponse,
        SearchPostsResponse,
        GetPostResponse,
        GetArticleResponse,
        GetArticleCommentsResponse
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    ) 


    