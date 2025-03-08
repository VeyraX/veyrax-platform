from googleapiclient.discovery import build
from typing import Optional, Dict, Any, List
from youtube_transcript_api import YouTubeTranscriptApi

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
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
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
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error getting captions for video {video_id}: {str(e)}")
            return {
                'items': [],
                'kind': 'youtube#captionListResponse',
                'etag': '',
                'pageInfo': {
                    'totalResults': 0,
                    'resultsPerPage': 0
                }
            }
    
    def get_caption_track(self, caption_id: str) -> str:
        try:
            parts = caption_id.split('_')
            if len(parts) >= 2:
                language_code = parts[-1]
                video_id = '_'.join(parts[:-1])
                
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
                
                transcript_text = ""
                for entry in transcript_data:
                    transcript_text += f"{entry['text']}\n"
                
                return transcript_text
            else:
                try:
                    return self.service.captions().download(id=caption_id).execute()
                except:
                    raise ValueError(f"Invalid caption ID format: {caption_id}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error getting caption track for ID {caption_id}: {str(e)}")
            return f"Error retrieving transcript: {str(e)}"