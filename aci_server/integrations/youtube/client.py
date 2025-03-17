from googleapiclient.discovery import build
from typing import Optional, Dict, Any, List
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Any, Optional
from ..common.proxy_utils import get_proxy_config



class YouTubeClient:
    def __init__(self, api_key: str):
        self.service = build('youtube', 'v3', developerKey=api_key)
    
    def search_videos(self, **kwargs) -> Dict[str, Any]:
        return self.service.search().list(
            part="snippet",
            type="video",
            **kwargs
        ).execute()
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        return self.service.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()
    
    def get_captions(self, video_id: str) -> Dict[str, Any]:
        proxies = get_proxy_config()
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
        
        items = []
        for transcript in transcript_list:
            items.append({
                'id': f"{video_id}_{transcript.language_code}", 
                'snippet': {
                    'language': transcript.language_code,
                    'name': transcript.language,
                    'trackKind': 'ASR' if transcript.is_generated else 'standard'
                }
            })
        
        return {
            'items': items,
            'kind': 'youtube#captionListResponse',
            'etag': '',
            'pageInfo': {
                'totalResults': len(items),
                'resultsPerPage': len(items)
            }
        }
    
    def get_caption_track(self, caption_id: str) -> str:
        parts = caption_id.split('_')
        if len(parts) >= 2:
            language_code = parts[-1]
            video_id = '_'.join(parts[:-1])
            
            proxies = get_proxy_config()
            transcript_data = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=[language_code], 
                proxies=proxies
            ) 
            
            transcript_text = ""
            for entry in transcript_data:
                transcript_text += f"{entry['text']}\n"
            
            return transcript_text
        else:
            try:
                return self.service.captions().download(id=caption_id).execute()
            except:
                raise ValueError(f"Invalid caption ID format: {caption_id}")
    
    def get_transcript(self, video_id: str, language: Optional[str] = None) -> str:
        proxies = get_proxy_config()

        if language:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[language], proxies=proxies)
        else:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
        
        transcript_text = ""
        for entry in transcript_data:
            transcript_text += f"{entry['text']}\n"
        
        return transcript_text