"""
YouTube Analytics Data Pipeline DAG
Orchestrates the entire ETL process: Extract → Load → Transform
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add src to path
sys.path.insert(0, '/opt/airflow/src')

# Default arguments
default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'youtube_analytics_pipeline',
    default_args=default_args,
    description='End-to-end YouTube data pipeline',
    schedule='0 6 * * *',  # Daily at 6 AM
    catchup=False,
    tags=['youtube', 'analytics', 'etl'],
)


def extract_youtube_data(**context):
    """Extract data from YouTube API and save to S3."""
    from extractors.youtube_extractor import YouTubeExtractor
    from utils.aws_utils import S3Handler
    from datetime import datetime, timezone
    
    print("="*70)
    print("EXTRACTING YOUTUBE DATA")
    print("="*70)
    
    extractor = YouTubeExtractor()
    s3 = S3Handler()
    
    # Ensure bucket exists
    s3.create_bucket_if_not_exists()
    
    timestamp = datetime.now(timezone.utc)
    regions = ['US']
    
    for region in regions:
        # Extract trending videos
        videos = extractor.get_trending_videos(region_code=region, max_results=50)
        
        if not videos:
            print(f"No videos found for {region}")
            continue
        
        # Get channels
        channel_ids = list(set([v['snippet']['channelId'] for v in videos]))
        channels = extractor.get_channel_info(channel_ids)
        
        # Package data
        data_package = {
            'extraction_metadata': {
                'timestamp': timestamp.isoformat(),
                'region': region,
                'video_count': len(videos),
                'channel_count': len(channels),
            },
            'trending_videos': videos,
            'channels': channels
        }
        
        # Upload to S3
        s3_key = s3.generate_s3_path(
            layer='bronze',
            data_type='trending_videos',
            region=region,
            timestamp=timestamp
        )
        
        s3.upload_json(data=data_package, s3_key=s3_key)
        print(f"✅ Uploaded {len(videos)} videos to S3")
    
    # Extract categories
    categories = extractor.get_video_categories('US')
    cat_data = {
        'extraction_metadata': {
            'timestamp': timestamp.isoformat(),
            'region': 'US',
            'category_count': len(categories)
        },
        'categories': categories
    }
    
    cat_key = s3.generate_s3_path(
        layer='bronze',
        data_type='video_categories',
        region='US',
        timestamp=timestamp
    )
    
    s3.upload_json(data=cat_data, s3_key=cat_key)
    print(f"✅ Uploaded {len(categories)} categories to S3")
    
    # Push metadata to XCom
    context['task_instance'].xcom_push(key='extraction_timestamp', value=timestamp.isoformat())
    context['task_instance'].xcom_push(key='video_count', value=len(videos))


def load_to_snowflake(**context):
    """Load data from S3 to Snowflake."""
    from utils.snowflake_utils import SnowflakeHandler
    
    print("="*70)
    print("LOADING DATA TO SNOWFLAKE")
    print("="*70)
    
    sf = SnowflakeHandler()
    
    if not sf.connect():
        raise Exception("Failed to connect to Snowflake")
    
    # TRUNCATE tables first to avoid duplicates
    print("Truncating tables to remove old data...")
    sf.execute_query("TRUNCATE TABLE RAW.TRENDING_VIDEOS_RAW")
    print("✅ Truncated TRENDING_VIDEOS_RAW")
    
    sf.execute_query("TRUNCATE TABLE RAW.VIDEO_CATEGORIES_RAW")
    print("✅ Truncated VIDEO_CATEGORIES_RAW")
    
    # Load trending videos
    sf.load_from_s3(
        s3_path='trending_videos/',
        table_name='RAW.TRENDING_VIDEOS_RAW',
        file_format='JSON'
    )
    
    # Load categories
    sf.load_from_s3(
        s3_path='video_categories/',
        table_name='RAW.VIDEO_CATEGORIES_RAW',
        file_format='JSON'
    )
    
    # Get row counts
    video_count = sf.get_row_count('RAW.TRENDING_VIDEOS_RAW')
    cat_count = sf.get_row_count('RAW.VIDEO_CATEGORIES_RAW')
    
    sf.close()
    
    print(f"✅ Loaded {video_count} video files and {cat_count} category files")


def setup_dbt_profiles():
    """Setup dbt profiles.yml in the container."""
    from pathlib import Path
    
    dest_dir = Path('/home/airflow/.dbt')
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    profiles_content = """youtube_analytics:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: """ + os.getenv('SNOWFLAKE_ACCOUNT') + """
      user: """ + os.getenv('SNOWFLAKE_USER') + """
      password: """ + os.getenv('SNOWFLAKE_PASSWORD') + """
      role: """ + os.getenv('SNOWFLAKE_ROLE') + """
      database: """ + os.getenv('SNOWFLAKE_DATABASE') + """
      warehouse: """ + os.getenv('SNOWFLAKE_WAREHOUSE') + """
      schema: STAGING
      threads: 4
"""
    
    dest_file = dest_dir / 'profiles.yml'
    with open(dest_file, 'w') as f:
        f.write(profiles_content)
    
    print(f"✅ Created dbt profiles.yml at {dest_file}")


# Define tasks
extract_task = PythonOperator(
    task_id='extract_youtube_data',
    python_callable=extract_youtube_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_snowflake',
    python_callable=load_to_snowflake,
    dag=dag,
)

setup_dbt_task = PythonOperator(
    task_id='setup_dbt_profiles',
    python_callable=setup_dbt_profiles,
    dag=dag,
)

# Use --full-refresh to rebuild all models from scratch
dbt_run_task = BashOperator(
    task_id='dbt_run_models',
    bash_command='cd /opt/airflow/dbt/youtube_analytics && dbt run --full-refresh',
    dag=dag,
)

dbt_test_task = BashOperator(
    task_id='dbt_test_models',
    bash_command='cd /opt/airflow/dbt/youtube_analytics && dbt test',
    dag=dag,
)

# Define task dependencies
extract_task >> load_task >> setup_dbt_task >> dbt_run_task >> dbt_test_task
