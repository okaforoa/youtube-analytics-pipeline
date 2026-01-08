"""Clear Snowflake data before fresh load."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.snowflake_utils import SnowflakeHandler

sf = SnowflakeHandler()

if sf.connect():
    print("Truncating tables...")
    sf.execute_query("TRUNCATE TABLE RAW.TRENDING_VIDEOS_RAW")
    sf.execute_query("TRUNCATE TABLE RAW.VIDEO_CATEGORIES_RAW")
    sf.close()
    print("✅ Tables cleared!")
