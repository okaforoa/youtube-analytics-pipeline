"""Snowflake utilities for loading and querying data."""
import snowflake.connector
from typing import List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config


class SnowflakeHandler:
    """Handle Snowflake operations for the data pipeline."""
    
    def __init__(self):
        """Initialize Snowflake connection."""
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish connection to Snowflake."""
        try:
            self.connection = snowflake.connector.connect(
                account=config.snowflake.account,
                user=config.snowflake.user,
                password=config.snowflake.password,
                warehouse=config.snowflake.warehouse,
                database=config.snowflake.database,
                schema=config.snowflake.schema_name,
                role=config.snowflake.role
            )
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to Snowflake")
            print(f"   Database: {config.snowflake.database}")
            print(f"   Schema: {config.snowflake.schema_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to Snowflake: {e}")
            return False
    
    def execute_query(self, query: str, fetch: bool = False) -> Any:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            fetch: Whether to fetch results
            
        Returns:
            Query results if fetch=True, None otherwise
        """
        try:
            self.cursor.execute(query)
            
            if fetch:
                results = self.cursor.fetchall()
                return results
            
            return None
            
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            print(f"Query: {query[:200]}...")
            return None
    
    def load_from_s3(
        self,
        s3_path: str,
        table_name: str,
        file_format: str = 'JSON'
    ) -> bool:
        """
        Load data from S3 into Snowflake table.
        
        Args:
            s3_path: S3 path (e.g., 'trending_videos/region=US/2026/01/03/')
            table_name: Target table name
            file_format: File format (JSON, CSV, PARQUET)
            
        Returns:
            True if successful
        """
        print(f"\nLoading data from S3 to {table_name}...")
        print(f"S3 Path: {s3_path}")
        
        try:
            # Create file format if it doesn't exist
            create_format_sql = f"""
            CREATE FILE FORMAT IF NOT EXISTS {file_format}_FORMAT
            TYPE = '{file_format}'
            STRIP_OUTER_ARRAY = TRUE
            """
            self.execute_query(create_format_sql)
            
            # Copy data from S3
            copy_sql = f"""
            COPY INTO {table_name} (FILENAME, RAW_DATA)
            FROM (
                SELECT 
                    METADATA$FILENAME,
                    $1
                FROM @S3_STAGE/{s3_path}
            )
            FILE_FORMAT = {file_format}_FORMAT
            ON_ERROR = 'CONTINUE'
            """
            
            self.cursor.execute(copy_sql)
            
            # Get results
            rows_loaded = self.cursor.rowcount
            
            print(f"✅ Loaded {rows_loaded} files into {table_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading from S3: {e}")
            return False
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for a table."""
        try:
            result = self.execute_query(
                f"SELECT COUNT(*) FROM {table_name}",
                fetch=True
            )
            return result[0][0] if result else 0
            
        except Exception as e:
            print(f"❌ Error getting row count: {e}")
            return 0
    
    def preview_table(self, table_name: str, limit: int = 5):
        """Preview table contents."""
        try:
            print(f"\n{'='*70}")
            print(f"Preview: {table_name} (first {limit} rows)")
            print(f"{'='*70}")
            
            result = self.execute_query(
                f"SELECT * FROM {table_name} LIMIT {limit}",
                fetch=True
            )
            
            if result:
                for i, row in enumerate(result, 1):
                    print(f"\nRow {i}:")
                    print(f"  Filename: {row[0]}")
                    print(f"  Loaded At: {row[4]}")
            else:
                print("No data found")
                
        except Exception as e:
            print(f"❌ Error previewing table: {e}")
    
    def close(self):
        """Close Snowflake connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("\n✅ Snowflake connection closed")


if __name__ == "__main__":
    # Test Snowflake handler
    print("=" * 70)
    print("SNOWFLAKE HANDLER TEST")
    print("=" * 70)
    
    sf = SnowflakeHandler()
    
    # Connect
    if sf.connect():
        
        # Check tables
        print("\n1. Checking tables...")
        sf.execute_query("SHOW TABLES IN SCHEMA RAW")
        
        # Check stage
        print("\n2. Checking S3 stage...")
        sf.execute_query("SHOW STAGES IN SCHEMA RAW")
        
        # List files in stage
        print("\n3. Listing files in S3 stage...")
        result = sf.execute_query(
            "LIST @S3_STAGE/trending_videos/",
            fetch=True
        )
        
        if result:
            print(f"Found {len(result)} files in S3 stage")
            for file in result[:3]:
                print(f"  - {file[0]}")
        
        sf.close()
    
    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)

    def truncate_table(self, table_name: str) -> bool:
        """Truncate a table."""
        try:
            self.execute_query(f"TRUNCATE TABLE {table_name}")
            print(f"✅ Truncated {table_name}")
            return True
        except Exception as e:
            print(f"❌ Error truncating {table_name}: {e}")
            return False

    def truncate_table(self, table_name: str) -> bool:
        """Truncate a table to remove all data."""
        try:
            self.execute_query(f"TRUNCATE TABLE {table_name}")
            print(f"✅ Truncated {table_name}")
            return True
        except Exception as e:
            print(f"❌ Error truncating {table_name}: {e}")
            return False
