"""AWS S3 utilities for data storage."""
import json
import boto3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config


class S3Handler:
    """Handle S3 operations for the data pipeline."""
    
    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            region_name=config.aws.region
        )
        self.bucket_name = config.aws.bucket_name
        
    def create_bucket_if_not_exists(self):
        """Create S3 bucket if it doesn't exist."""
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' already exists")
            
        except:
            print(f"Creating bucket '{self.bucket_name}'...")
            
            try:
                if config.aws.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': config.aws.region}
                    )
                print(f"✅ Bucket '{self.bucket_name}' created successfully")
                
            except Exception as e:
                print(f"❌ Error creating bucket: {e}")
                raise
    
    def upload_json(
        self, 
        data: Dict[Any, Any], 
        s3_key: str,
        metadata: Dict[str, str] = None
    ) -> bool:
        """
        Upload JSON data to S3.
        
        Args:
            data: Dictionary to upload
            s3_key: S3 object key (path)
            metadata: Optional metadata tags
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'Body': json_data.encode('utf-8'),
                'ContentType': 'application/json'
            }
            
            if metadata:
                upload_params['Metadata'] = metadata
            
            self.s3_client.put_object(**upload_params)
            
            print(f"✅ Uploaded to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading to S3: {e}")
            return False
    
    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Upload a local file to S3.
        
        Args:
            local_path: Path to local file
            s3_key: S3 object key (path)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            print(f"✅ Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return False
    
    def download_json(self, s3_key: str) -> Dict:
        """
        Download JSON data from S3.
        
        Args:
            s3_key: S3 object key (path)
            
        Returns:
            Dictionary with data
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            data = json.loads(response['Body'].read().decode('utf-8'))
            print(f"✅ Downloaded from s3://{self.bucket_name}/{s3_key}")
            return data
            
        except Exception as e:
            print(f"❌ Error downloading from S3: {e}")
            return {}
    
    def list_objects(self, prefix: str = '') -> list:
        """
        List objects in S3 with given prefix.
        
        Args:
            prefix: S3 key prefix to filter
            
        Returns:
            List of object keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                keys = [obj['Key'] for obj in response['Contents']]
                print(f"✅ Found {len(keys)} objects with prefix '{prefix}'")
                return keys
            else:
                print(f"No objects found with prefix '{prefix}'")
                return []
                
        except Exception as e:
            print(f"❌ Error listing objects: {e}")
            return []
    
    def generate_s3_path(
        self,
        layer: str,
        data_type: str,
        region: str = None,
        timestamp: datetime = None
    ) -> str:
        """
        Generate standardized S3 path for bronze/silver/gold layers.
        
        Args:
            layer: 'bronze', 'silver', or 'gold'
            data_type: Type of data (e.g., 'trending_videos', 'channels')
            region: Optional region code
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            S3 key path
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        date_path = timestamp.strftime('%Y/%m/%d')
        time_str = timestamp.strftime('%Y%m%d_%H%M%S')
        
        path_parts = [layer, data_type]
        
        if region:
            path_parts.append(f'region={region}')
        
        path_parts.append(date_path)
        path_parts.append(f'{data_type}_{time_str}.json')
        
        return '/'.join(path_parts)


if __name__ == "__main__":
    # Test S3 handler
    print("=" * 60)
    print("S3 HANDLER TEST")
    print("=" * 60)
    
    s3 = S3Handler()
    
    # Test 1: Create bucket
    print("\n1. Checking/creating S3 bucket...")
    s3.create_bucket_if_not_exists()
    
    # Test 2: Upload sample data
    print("\n2. Testing upload...")
    test_data = {
        'test': 'data',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'YouTube analytics pipeline test'
    }
    
    test_key = s3.generate_s3_path(
        layer='bronze',
        data_type='test',
        region='US'
    )
    
    success = s3.upload_json(test_data, test_key)
    
    if success:
        # Test 3: Download data
        print("\n3. Testing download...")
        downloaded = s3.download_json(test_key)
        print(f"Downloaded data: {downloaded}")
        
        # Test 4: List objects
        print("\n4. Testing list objects...")
        objects = s3.list_objects(prefix='bronze/test')
        for obj in objects:
            print(f"  - {obj}")
    
    print("\n" + "=" * 60)
    print("✅ S3 Handler test complete!")
    print("=" * 60)
