"""YouTube data extractor for trending videos and analytics."""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config


class YouTubeExtractor:
    """Extract data from YouTube Data API v3."""
    
    def __init__(self):
        """Initialize YouTube API client."""
        self.youtube = build('youtube', 'v3', developerKey=config.youtube.api_key)
        self.quota_used = 0  # Track API quota usage
        
    def get_trending_videos(
        self, 
        region_code: str = 'US', 
        max_results: int = 50,
        category_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get trending videos for a region.
        
        Args:
            region_code: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'IN')
            max_results: Number of videos to retrieve (max 50 per request)
            category_id: Optional category ID to filter by
            
        Returns:
            List of video dictionaries with full metadata
        """
        print(f"Fetching trending videos for region: {region_code}")
        
        try:
            request_params = {
                'part': 'snippet,contentDetails,statistics',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': min(max_results, 50)
            }
            
            if category_id:
                request_params['videoCategoryId'] = category_id
            
            request = self.youtube.videos().list(**request_params)
            response = request.execute()
            
            # Quota cost: 1 unit
            self.quota_used += 1
            
            videos = response.get('items', [])
            print(f"✅ Retrieved {len(videos)} trending videos")
            
            return videos
            
        except HttpError as e:
            print(f"❌ Error fetching trending videos: {e}")
            return []
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        Get detailed information for specific videos.
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of detailed video dictionaries
        """
        if not video_ids:
            return []
        
        print(f"Fetching details for {len(video_ids)} videos")
        
        try:
            # YouTube API accepts max 50 IDs per request
            all_videos = []
            
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i + 50]
                
                request = self.youtube.videos().list(
                    part='snippet,contentDetails,statistics,status',
                    id=','.join(batch)
                )
                response = request.execute()
                
                # Quota cost: 1 unit per request
                self.quota_used += 1
                
                all_videos.extend(response.get('items', []))
                
                # Rate limiting - be nice to the API
                if i + 50 < len(video_ids):
                    time.sleep(0.1)
            
            print(f"✅ Retrieved details for {len(all_videos)} videos")
            return all_videos
            
        except HttpError as e:
            print(f"❌ Error fetching video details: {e}")
            return []
    
    def get_channel_info(self, channel_ids: List[str]) -> List[Dict]:
        """
        Get channel information.
        
        Args:
            channel_ids: List of YouTube channel IDs
            
        Returns:
            List of channel dictionaries
        """
        if not channel_ids:
            return []
        
        # Remove duplicates
        channel_ids = list(set(channel_ids))
        
        print(f"Fetching info for {len(channel_ids)} channels")
        
        try:
            all_channels = []
            
            for i in range(0, len(channel_ids), 50):
                batch = channel_ids[i:i + 50]
                
                request = self.youtube.channels().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch)
                )
                response = request.execute()
                
                # Quota cost: 1 unit per request
                self.quota_used += 1
                
                all_channels.extend(response.get('items', []))
                
                if i + 50 < len(channel_ids):
                    time.sleep(0.1)
            
            print(f"✅ Retrieved info for {len(all_channels)} channels")
            return all_channels
            
        except HttpError as e:
            print(f"❌ Error fetching channel info: {e}")
            return []
    
    def get_video_categories(self, region_code: str = 'US') -> List[Dict]:
        """
        Get available video categories for a region.
        
        Args:
            region_code: ISO 3166-1 alpha-2 country code
            
        Returns:
            List of category dictionaries
        """
        print(f"Fetching video categories for region: {region_code}")
        
        try:
            request = self.youtube.videoCategories().list(
                part='snippet',
                regionCode=region_code
            )
            response = request.execute()
            
            # Quota cost: 1 unit
            self.quota_used += 1
            
            categories = response.get('items', [])
            print(f"✅ Retrieved {len(categories)} categories")
            
            return categories
            
        except HttpError as e:
            print(f"❌ Error fetching categories: {e}")
            return []
    
    def search_videos(
        self,
        query: str,
        max_results: int = 50,
        order: str = 'relevance',
        published_after: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Search for videos.
        
        Args:
            query: Search query string
            max_results: Number of results (max 50)
            order: Sort order ('relevance', 'date', 'viewCount', 'rating')
            published_after: Only return videos published after this date
            
        Returns:
            List of search result dictionaries
        """
        print(f"Searching for: '{query}'")
        
        try:
            request_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order
            }
            
            if published_after:
                request_params['publishedAfter'] = published_after.isoformat() + 'Z'
            
            request = self.youtube.search().list(**request_params)
            response = request.execute()
            
            # Quota cost: 100 units (search is expensive!)
            self.quota_used += 100
            
            results = response.get('items', [])
            print(f"✅ Found {len(results)} videos")
            
            return results
            
        except HttpError as e:
            print(f"❌ Error searching videos: {e}")
            return []
    
    def get_quota_usage(self) -> int:
        """Return estimated quota units used in this session."""
        return self.quota_used
    
    def save_to_json(self, data: Dict, filepath: str):
        """
        Save data to JSON file.
        
        Args:
            data: Dictionary to save
            filepath: Path to save file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved data to: {filepath}")


if __name__ == "__main__":
    # Test the extractor
    print("=" * 60)
    print("YOUTUBE EXTRACTOR TEST")
    print("=" * 60)
    
    extractor = YouTubeExtractor()
    
    # Test 1: Get trending videos
    print("\n1. Testing trending videos extraction...")
    trending = extractor.get_trending_videos(region_code='US', max_results=10)
    
    if trending:
        print(f"\nSample trending video:")
        video = trending[0]
        print(f"  Title: {video['snippet']['title']}")
        print(f"  Channel: {video['snippet']['channelTitle']}")
        print(f"  Views: {int(video['statistics']['viewCount']):,}")
        print(f"  Likes: {int(video['statistics'].get('likeCount', 0)):,}")
        print(f"  Published: {video['snippet']['publishedAt']}")
    
    # Test 2: Get channel info
    print("\n2. Testing channel info extraction...")
    if trending:
        channel_ids = [v['snippet']['channelId'] for v in trending[:5]]
        channels = extractor.get_channel_info(channel_ids)
        
        if channels:
            print(f"\nSample channel:")
            channel = channels[0]
            print(f"  Name: {channel['snippet']['title']}")
            print(f"  Subscribers: {int(channel['statistics'].get('subscriberCount', 0)):,}")
            print(f"  Total Views: {int(channel['statistics']['viewCount']):,}")
            print(f"  Videos: {int(channel['statistics']['videoCount']):,}")
    
    # Test 3: Get categories
    print("\n3. Testing categories extraction...")
    categories = extractor.get_video_categories('US')
    if categories:
        print(f"\nAvailable categories: {len(categories)}")
        for cat in categories[:5]:
            print(f"  - {cat['snippet']['title']}")
    
    print(f"\n" + "=" * 60)
    print(f"Quota used this session: ~{extractor.get_quota_usage()} units")
    print(f"Daily quota limit: 10,000 units")
    print(f"Remaining: ~{10000 - extractor.get_quota_usage()} units")
    print("=" * 60)
    print("\n✅ Extractor test complete!")
