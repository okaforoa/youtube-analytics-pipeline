"""Clear all Snowflake tables for fresh pipeline run."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.snowflake_utils import SnowflakeHandler

sf = SnowflakeHandler()

if sf.connect():
    print("Clearing all tables...")
    
    # RAW layer
    sf.execute_query("TRUNCATE TABLE RAW.TRENDING_VIDEOS_RAW")
    print("✅ Cleared RAW.TRENDING_VIDEOS_RAW")
    
    sf.execute_query("TRUNCATE TABLE RAW.VIDEO_CATEGORIES_RAW")
    print("✅ Cleared RAW.VIDEO_CATEGORIES_RAW")
    
    # STAGING layer
    sf.execute_query("DROP TABLE IF EXISTS STAGING.STG_VIDEOS")
    print("✅ Dropped STAGING.STG_VIDEOS")
    
    sf.execute_query("DROP TABLE IF EXISTS STAGING.STG_CHANNELS")
    print("✅ Dropped STAGING.STG_CHANNELS")
    
    sf.execute_query("DROP TABLE IF EXISTS STAGING.STG_CATEGORIES")
    print("✅ Dropped STAGING.STG_CATEGORIES")
    
    # MARTS layer
    sf.execute_query("DROP TABLE IF EXISTS MARTS.DIM_VIDEOS")
    print("✅ Dropped MARTS.DIM_VIDEOS")
    
    sf.execute_query("DROP TABLE IF EXISTS MARTS.DIM_CHANNELS")
    print("✅ Dropped MARTS.DIM_CHANNELS")
    
    sf.execute_query("DROP TABLE IF EXISTS MARTS.DIM_CATEGORIES")
    print("✅ Dropped MARTS.DIM_CATEGORIES")
    
    sf.execute_query("DROP TABLE IF EXISTS MARTS.FACT_VIDEO_PERFORMANCE")
    print("✅ Dropped MARTS.FACT_VIDEO_PERFORMANCE")
    
    sf.close()
    print("\n🎉 All tables cleared! Ready for fresh pipeline run.")
else:
    print("❌ Failed to connect to Snowflake")
