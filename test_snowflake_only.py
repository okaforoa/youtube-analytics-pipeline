"""Debug Snowflake connection."""
import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

# Print what we're trying to connect with (masked)
print("Attempting Snowflake connection with:")
print(f"  Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
print(f"  User: {os.getenv('SNOWFLAKE_USER')}")
print(f"  Password: {'*' * len(os.getenv('SNOWFLAKE_PASSWORD', ''))}")
print(f"  Warehouse: {os.getenv('SNOWFLAKE_WAREHOUSE')}")
print(f"  Database: {os.getenv('SNOWFLAKE_DATABASE')}")
print()

try:
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        login_timeout=30,
    )
    print("✅ Connection successful!")

    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()[0]
    print(f"✅ Snowflake version: {version}")

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Connection failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")

    # Try to get more details
    if hasattr(e, "errno"):
        print(f"Error code: {e.errno}")
    if hasattr(e, "msg"):
        print(f"Message: {e.msg}")
    if hasattr(e, "sqlstate"):
        print(f"SQL State: {e.sqlstate}")

    print()
    print("Troubleshooting:")
    print("1. Verify you can log into https://app.snowflake.com/vihujuv/db16339/")
    print("2. Try account format: 'vihujuv-db16339' (current in .env)")
    print("3. Check network/firewall - Snowflake requires port 443")
    print("4. Verify username is correct (case-sensitive)")
