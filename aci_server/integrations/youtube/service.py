from typing import Optional, Dict, Any, Union, List
from .client import YouTubeClient
from .schema import (
    VideoList, Video, CaptionList, Caption, Transcription, 
    SearchFilters, ApiResponse
)
from dateutil import parser
import os
import re
from ..common.component_handler import load_components, prepare_components_auto

class YouTubeService:
    def __init__(self, client: YouTubeClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[Video, VideoList, CaptionList, Transcription], component_name: str = None) -> ApiResponse:
        tool_name = "youtube"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _generate_html_link(self, video_id: str) -> str:
        return f"https://www.youtube.com/watch?v={video_id}"

    def _parse_duration(self, duration_str: str) -> str:
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if not match:
            return duration_str
            
        hours, minutes, seconds = match.groups()
        result = ""
        if hours:
            result += f"{hours}:"
        if minutes:
            if hours and len(minutes) == 1:
                minutes = f"0{minutes}"
            result += f"{minutes}:"
        else:
            result += "00:"
        if seconds:
            if len(seconds) == 1:
                seconds = f"0{seconds}"
            result += seconds
        else:
            result += "00"
            
        return result

    def search_videos(self, filters: SearchFilters, page_token: Optional[str] = None) -> ApiResponse:
        params = {
            "q": filters.query,
            "maxResults": filters.max_results,
            "pageToken": page_token
        }
        
        if filters.published_after:
            params["publishedAfter"] = filters.published_after
        if filters.published_before:
            params["publishedBefore"] = filters.published_before
        if filters.channel_id:
            params["channelId"] = filters.channel_id
        if filters.order:
            params["order"] = filters.order
            
        response = self.client.search_videos(**params)
        videos = []
        
        for item in response.get('items', []):
            if item['id']['kind'] == 'youtube#video':
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                videos.append({
                    'id': video_id,
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'published_at': parser.parse(snippet.get('publishedAt')),
                    'channel_title': snippet.get('channelTitle', ''),
                    'channel_id': snippet.get('channelId', '')
                })
                
        video_list = VideoList(
            videos=videos,
            next_page_token=response.get('nextPageToken'),
            total_results=response.get('pageInfo', {}).get('totalResults')
        )
        
        return self.prepare_response(video_list, "YouTubeVideoList")

    def get_video(self, video_id: str) -> ApiResponse:
        response = self.client.get_video_details(video_id)
        
        if not response.get('items'):
            raise ValueError(f"Video with ID {video_id} not found")
            
        video_data = response['items'][0]
        snippet = video_data.get('snippet', {})
        statistics = video_data.get('statistics', {})
        content_details = video_data.get('contentDetails', {})
        
        video = Video(
            id=video_id,
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            published_at=parser.parse(snippet.get('publishedAt')),
            channel_title=snippet.get('channelTitle', ''),
            channel_id=snippet.get('channelId', ''),
            view_count=int(statistics.get('viewCount', 0)),
            like_count=int(statistics.get('likeCount', 0)),
            comment_count=int(statistics.get('commentCount', 0)),
            duration=self._parse_duration(content_details.get('duration', '')),
            html_link=self._generate_html_link(video_id)
        )
        
        return self.prepare_response(video, "YouTubeVideoCard")

    def get_captions(self, video_id: str) -> ApiResponse:
        response = self.client.get_captions(video_id)
        captions = []
        
        for item in response.get('items', []):
            snippet = item.get('snippet', {})
            captions.append(Caption(
                id=item['id'],
                language=snippet.get('language', ''),
                name=snippet.get('name', ''),
                is_auto=snippet.get('trackKind', '') == 'ASR'
            ))
            
        caption_list = CaptionList(
            captions=captions,
            video_id=video_id
        )
        
        return self.prepare_response(caption_list, "YouTubeCaptionList")

    def get_transcription(self, video_id: str, caption_id: Optional[str] = None, language: Optional[str] = None) -> ApiResponse:
        if not caption_id:
            captions_response = self.client.get_captions(video_id)
            captions = captions_response.get('items', [])
            
            if not captions:
                raise ValueError(f"No captions found for video {video_id}")
                
            if language:
                caption = next((c for c in captions if c['snippet']['language'] == language), None)
                if not caption:
                    raise ValueError(f"No caption found for language {language}")
            else:
                caption = captions[0]
                
            caption_id = caption['id']
            language = caption['snippet']['language']
        
        caption_text = self.client.get_caption_track(caption_id)
        
        transcription = Transcription(
            video_id=video_id,
            caption_id=caption_id,
            text=caption_text,
            language=language
        )
        
        return self.prepare_response(transcription, "YouTubeTranscription")