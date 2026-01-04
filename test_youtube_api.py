"""Test YouTube API connection."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

print("Testing YouTube API Connection\n")
print(f"API Key: {config.youtube.api_key[:15]}...\n")

try:
    # Build YouTube API client
    youtube = build('youtube', 'v3', developerKey=config.youtube.api_key)
    
    # Test with a simple request - get trending videos in US
    print("Fetching trending videos to test API...")
    request = youtube.videos().list(
        part='snippet,statistics',
        chart='mostPopular',
        regionCode='US',
        maxResults=5
    )
    response = request.execute()
    
    print(f"\n✅ YouTube API Connected Successfully!\n")
    print(f"Retrieved {len(response['items'])} trending videos:")
    print("-" * 60)
    
    for i, video in enumerate(response['items'], 1):
        title = video['snippet']['title']
        channel = video['snippet']['channelTitle']
        views = int(video['statistics']['viewCount'])
        
        print(f"{i}. {title}")
        print(f"   Channel: {channel}")
        print(f"   Views: {views:,}")
        print()
    
    print("=" * 60)
    print("✅ YouTube API is working perfectly!")
    print("Ready to start building the data pipeline!")
    
except HttpError as e:
    print(f"❌ YouTube API Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check that API key is correct in .env")
    print("2. Verify YouTube Data API v3 is enabled in Google Cloud")
    print("3. Make sure API key restrictions allow YouTube Data API v3")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"Error type: {type(e).__name__}")

