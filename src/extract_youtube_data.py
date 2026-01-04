"""Main script to extract YouTube data and save to S3."""
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from extractors.youtube_extractor import YouTubeExtractor
from utils.aws_utils import S3Handler
from config import config


def extract_trending_videos(regions: list = ['US'], max_results: int = 50):
    """
    Extract trending videos for specified regions and save to S3.
    
    Args:
        regions: List of region codes (e.g., ['US', 'GB', 'IN'])
        max_results: Number of videos per region
    """
    print("=" * 70)
    print("YOUTUBE TRENDING VIDEOS EXTRACTION")
    print("=" * 70)
    
    # Initialize
    extractor = YouTubeExtractor()
    s3 = S3Handler()
    
    # Ensure bucket exists
    s3.create_bucket_if_not_exists()
    
    timestamp = datetime.now(timezone.utc)
    
    for region in regions:
        print(f"\n{'='*70}")
        print(f"Processing region: {region}")
        print(f"{'='*70}")
        
        # Extract trending videos
        trending_videos = extractor.get_trending_videos(
            region_code=region,
            max_results=max_results
        )
        
        if not trending_videos:
            print(f"⚠️  No trending videos found for {region}")
            continue
        
        # Extract channel IDs
        channel_ids = list(set([
            video['snippet']['channelId'] 
            for video in trending_videos
        ]))
        
        # Get channel information
        channels = extractor.get_channel_info(channel_ids)
        
        # Prepare data package
        data_package = {
            'extraction_metadata': {
                'timestamp': timestamp.isoformat(),
                'region': region,
                'video_count': len(trending_videos),
                'channel_count': len(channels),
                'quota_used': extractor.get_quota_usage()
            },
            'trending_videos': trending_videos,
            'channels': channels
        }
        
        # Generate S3 path
        s3_key = s3.generate_s3_path(
            layer='bronze',
            data_type='trending_videos',
            region=region,
            timestamp=timestamp
        )
        
        # Upload to S3
        success = s3.upload_json(
            data=data_package,
            s3_key=s3_key,
            metadata={
                'region': region,
                'video_count': str(len(trending_videos)),
                'extraction_timestamp': timestamp.isoformat()
            }
        )
        
        if success:
            print(f"\n✅ Successfully processed {region}:")
            print(f"   Videos: {len(trending_videos)}")
            print(f"   Channels: {len(channels)}")
            print(f"   S3 Key: {s3_key}")
        else:
            print(f"\n❌ Failed to upload data for {region}")
    
    print(f"\n{'='*70}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*70}")
    print(f"Total API quota used: ~{extractor.get_quota_usage()} units")
    print(f"Remaining daily quota: ~{10000 - extractor.get_quota_usage()} units")
    print(f"{'='*70}")


def extract_video_categories(region: str = 'US'):
    """
    Extract video categories and save to S3.
    
    Args:
        region: Region code
    """
    print("=" * 70)
    print("YOUTUBE VIDEO CATEGORIES EXTRACTION")
    print("=" * 70)
    
    extractor = YouTubeExtractor()
    s3 = S3Handler()
    
    timestamp = datetime.now(timezone.utc)
    
    # Extract categories
    categories = extractor.get_video_categories(region_code=region)
    
    if not categories:
        print(f"⚠️  No categories found for {region}")
        return
    
    # Prepare data package
    data_package = {
        'extraction_metadata': {
            'timestamp': timestamp.isoformat(),
            'region': region,
            'category_count': len(categories)
        },
        'categories': categories
    }
    
    # Generate S3 path
    s3_key = s3.generate_s3_path(
        layer='bronze',
        data_type='video_categories',
        region=region,
        timestamp=timestamp
    )
    
    # Upload to S3
    success = s3.upload_json(data=data_package, s3_key=s3_key)
    
    if success:
        print(f"\n✅ Successfully extracted {len(categories)} categories")
        print(f"   S3 Key: {s3_key}")
    
    print(f"\n{'='*70}")


if __name__ == "__main__":
    # Example: Extract trending videos for multiple regions
    print("\n🚀 Starting YouTube data extraction...\n")
    
    # Extract trending videos for US
    extract_trending_videos(regions=['US'], max_results=50)
    
    # Extract video categories
    extract_video_categories(region='US')
    
    print("\n✅ All extractions complete!")
