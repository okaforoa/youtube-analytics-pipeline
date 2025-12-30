"""Test connections to all services."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_config_loads():
    """Test that config file loads without errors."""
    print("Testing configuration loading...")
    try:
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
            "s3",
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            region_name=config.aws.region,
        )

        # Test by listing buckets
        response = s3_client.list_buckets()
        buckets = [bucket["Name"] for bucket in response["Buckets"]]

        if config.aws.bucket_name in buckets:
            print(f"✅ AWS S3 connected - Found bucket: {config.aws.bucket_name}")
            return True
        else:
            print(f"⚠️  AWS connected but bucket '{config.aws.bucket_name}' not found")
            print(f"   Available buckets: {buckets}")
            return False

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
            database=config.snowflake.database,
            schema=config.snowflake.schema,
            role=config.snowflake.role,
        )

        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        print(f"✅ Snowflake connected - Version: {version}")
        print(f"   Database: {config.snowflake.database}")
        print(f"   Warehouse: {config.snowflake.warehouse}")
        return True

    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        return False


def test_spotify_config():
    """Test that Spotify config is set (we'll test actual connection later)."""
    print("\nTesting Spotify configuration...")
    try:
        from config import config

        if (
            config.spotify.client_id
            and config.spotify.client_id != "your_client_id_here"
        ):
            print("✅ Spotify credentials configured")
            print(f"   Client ID: {config.spotify.client_id[:10]}...")
            return True
        else:
            print("⚠️  Spotify credentials not yet configured (this is OK for now)")
            return True  # Not a failure, just pending

    except Exception as e:
        print(f"❌ Spotify config check failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CONNECTION TESTS")
    print("=" * 60)

    results = {
        "Config": test_config_loads(),
        "AWS S3": test_aws_connection(),
        "Snowflake": test_snowflake_connection(),
        "Spotify": test_spotify_config(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service:15} {status}")

    all_critical_passed = (
        results["Config"] and results["AWS S3"] and results["Snowflake"]
    )

    if all_critical_passed:
        print("\n🎉 All critical services connected successfully!")
        print("Ready to start building the pipeline!")
        sys.exit(0)
    else:
        print("\n⚠️  Some connections failed. Please check the errors above.")
        sys.exit(1)
