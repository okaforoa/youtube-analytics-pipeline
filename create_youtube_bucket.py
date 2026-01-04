"""Create YouTube S3 bucket."""
import boto3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from config import config

print("Creating new YouTube S3 bucket...")
print(f"Bucket name: youtube-data-pipeline-dion")
print(f"Region: {config.aws.region}")

s3_client = boto3.client(
    's3',
    aws_access_key_id=config.aws.access_key_id,
    aws_secret_access_key=config.aws.secret_access_key,
    region_name=config.aws.region
)

try:
    if config.aws.region == 'us-east-1':
        s3_client.create_bucket(Bucket='youtube-data-pipeline-dion')
    else:
        s3_client.create_bucket(
            Bucket='youtube-data-pipeline-dion',
            CreateBucketConfiguration={'LocationConstraint': config.aws.region}
        )
    
    print("✅ Bucket 'youtube-data-pipeline-dion' created successfully!")
    
except s3_client.exceptions.BucketAlreadyOwnedByYou:
    print("✅ Bucket already exists and is owned by you")
    
except Exception as e:
    print(f"❌ Error creating bucket: {e}")
    sys.exit(1)
