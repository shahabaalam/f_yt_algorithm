import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_youtube_service():
    """Initialize YouTube API service"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY environment variable not set")
    
    return build('youtube', 'v3', developerKey=api_key)

def search_videos(query, max_results=10):
    """Search for videos on YouTube"""
    try:
        youtube = get_youtube_service()
        
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            order='relevance'
        ).execute()
        
        videos = []
        video_ids = []
        
        for search_result in search_response.get('items', []):
            video_id = search_result['id']['videoId']
            video_ids.append(video_id)
            
            video_data = {
                'id': video_id,
                'title': search_result['snippet']['title'],
                'description': search_result['snippet']['description'],
                'channel_title': search_result['snippet']['channelTitle'],
                'published_at': search_result['snippet']['publishedAt'],
                'thumbnail': search_result['snippet']['thumbnails']['medium']['url']
            }
            videos.append(video_data)
        
        # Get additional statistics for videos
        if video_ids:
            stats_response = youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            # Merge statistics with video data
            for video, stat_item in zip(videos, stats_response.get('items', [])):
                video['view_count'] = int(stat_item['statistics'].get('viewCount', 0))
                video['like_count'] = int(stat_item['statistics'].get('likeCount', 0))
                video['comment_count'] = int(stat_item['statistics'].get('commentCount', 0))
                video['duration'] = stat_item['contentDetails'].get('duration', '')
        
        return videos
        
    except HttpError as e:
        raise Exception(f"YouTube API error: {e.resp.status} - {e.content}")
    except Exception as e:
        raise Exception(f"Error searching videos: {str(e)}")

def get_video_details(video_id):
    """Get detailed information for a specific video"""
    try:
        youtube = get_youtube_service()
        
        response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            return None
            
        item = response['items'][0]
        
        return {
            'id': video_id,
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'channel_title': item['snippet']['channelTitle'],
            'published_at': item['snippet']['publishedAt'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'view_count': int(item['statistics'].get('viewCount', 0)),
            'like_count': int(item['statistics'].get('likeCount', 0)),
            'comment_count': int(item['statistics'].get('commentCount', 0)),
            'duration': item['contentDetails'].get('duration', ''),
            'tags': item['snippet'].get('tags', [])
        }
        
    except HttpError as e:
        raise Exception(f"YouTube API error: {e.resp.status} - {e.content}")
    except Exception as e:
        raise Exception(f"Error getting video details: {str(e)}")
