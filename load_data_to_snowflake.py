"""Load YouTube data from S3 to Snowflake."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.snowflake_utils import SnowflakeHandler


def load_all_data():
    """Load all YouTube data from S3 to Snowflake."""
    print("=" * 70)
    print("LOADING YOUTUBE DATA TO SNOWFLAKE")
    print("=" * 70)
    
    sf = SnowflakeHandler()
    
    if not sf.connect():
        print("❌ Failed to connect to Snowflake")
        return
    
    # Load trending videos
    print("\n1. Loading trending videos...")
    success1 = sf.load_from_s3(
        s3_path='trending_videos/',
        table_name='RAW.TRENDING_VIDEOS_RAW',
        file_format='JSON'
    )
    
    if success1:
        count = sf.get_row_count('RAW.TRENDING_VIDEOS_RAW')
        print(f"   Total rows in table: {count}")
        sf.preview_table('RAW.TRENDING_VIDEOS_RAW', limit=2)
    
    # Load video categories
    print("\n2. Loading video categories...")
    success2 = sf.load_from_s3(
        s3_path='video_categories/',
        table_name='RAW.VIDEO_CATEGORIES_RAW',
        file_format='JSON'
    )
    
    if success2:
        count = sf.get_row_count('RAW.VIDEO_CATEGORIES_RAW')
        print(f"   Total rows in table: {count}")
        sf.preview_table('RAW.VIDEO_CATEGORIES_RAW', limit=2)
    
    # Summary
    print("\n" + "=" * 70)
    print("LOAD SUMMARY")
    print("=" * 70)
    
    trending_count = sf.get_row_count('RAW.TRENDING_VIDEOS_RAW')
    categories_count = sf.get_row_count('RAW.VIDEO_CATEGORIES_RAW')
    
    print(f"Trending Videos: {trending_count} files loaded")
    print(f"Video Categories: {categories_count} files loaded")
    
    if trending_count > 0 and categories_count > 0:
        print("\n✅ All data loaded successfully to Snowflake!")
        print("   Bronze layer (RAW schema) is complete!")
    else:
        print("\n⚠️  Some tables have no data")
    
    sf.close()
    print("=" * 70)


if __name__ == "__main__":
    load_all_data()
