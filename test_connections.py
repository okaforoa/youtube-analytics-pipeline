"""Test connections to all services."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_loads():
    """Test that config file loads without errors."""
    print("Testing configuration loading...")
    try:
        from config import config
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False


def test_aws_connection():
    """Test AWS S3 connection."""
    print("\nTesting AWS S3 connection...")
    try:
        import boto3
        from config import config
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            region_name=config.aws.region
        )
        
        # Test by listing buckets
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        
        if config.aws.bucket_name in buckets:
            print(f"✅ AWS S3 connected - Found bucket: {config.aws.bucket_name}")
            return True
        else:
            print(f"⚠️  AWS connected but bucket '{config.aws.bucket_name}' not found")
            print(f"   Available buckets: {buckets}")
            print(f"   Note: You may need to create the new YouTube bucket")
            return True  # Still count as success since AWS connection works
            
    except Exception as e:
        print(f"❌ AWS connection failed: {e}")
        return False


def test_snowflake_connection():
    """Test Snowflake connection."""
    print("\nTesting Snowflake connection...")
    try:
        import snowflake.connector
        from config import config
        
        conn = snowflake.connector.connect(
            account=config.snowflake.account,
            user=config.snowflake.user,
            password=config.snowflake.password,
            warehouse=config.snowflake.warehouse,
            role=config.snowflake.role
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        
        # Check if YOUTUBE_DB exists, if not we'll create it later
        cursor.execute("SHOW DATABASES LIKE 'YOUTUBE_DB'")
        db_exists = len(cursor.fetchall()) > 0
        
        cursor.close()
        conn.close()
        
        print(f"✅ Snowflake connected - Version: {version}")
        if db_exists:
            print(f"   Database: YOUTUBE_DB exists")
        else:
            print(f"   Note: YOUTUBE_DB doesn't exist yet (will create later)")
        print(f"   Warehouse: {config.snowflake.warehouse}")
        return True
        
    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        return False


def test_youtube_config():
    """Test that YouTube config is set."""
    print("\nTesting YouTube configuration...")
    try:
        from config import config
        
        if (config.youtube.api_key and 
            config.youtube.api_key != "placeholder"):
            print(f"✅ YouTube API key configured")
            print(f"   API Key: {config.youtube.api_key[:10]}...")
            return True
        else:
            print("⚠️  YouTube API key not yet configured (add it when you get it from Google Cloud)")
            return True  # Not a failure, just pending
            
    except Exception as e:
        print(f"❌ YouTube config check failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CONNECTION TESTS - YOUTUBE ANALYTICS PIPELINE")
    print("=" * 60)
    
    results = {
        "Config": test_config_loads(),
        "AWS S3": test_aws_connection(),
        "Snowflake": test_snowflake_connection(),
        "YouTube": test_youtube_config()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service:15} {status}")
    
    all_critical_passed = results["Config"] and results["AWS S3"] and results["Snowflake"]
    
    if all_critical_passed:
        print("\n🎉 All critical services connected successfully!")
        print("Ready to start building the YouTube pipeline!")
        sys.exit(0)
    else:
        print("\n⚠️  Some connections failed. Please check the errors above.")
        sys.exit(1)
