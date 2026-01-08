"""Setup dbt profiles in Airflow container."""
import os
import shutil
from pathlib import Path

def setup_dbt_profiles():
    """Copy dbt profiles to the expected location."""
    # Source: where profiles.yml exists on your local machine
    source = Path.home() / '.dbt' / 'profiles.yml'
    
    # Destination: where dbt expects it in container
    dest_dir = Path('/home/airflow/.dbt')
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_file = dest_dir / 'profiles.yml'
    
    # For container, we'll create it programmatically
    profiles_content = """
youtube_analytics:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: {{ env_var('SNOWFLAKE_ACCOUNT') }}
      user: {{ env_var('SNOWFLAKE_USER') }}
      password: {{ env_var('SNOWFLAKE_PASSWORD') }}
      role: {{ env_var('SNOWFLAKE_ROLE') }}
      database: {{ env_var('SNOWFLAKE_DATABASE') }}
      warehouse: {{ env_var('SNOWFLAKE_WAREHOUSE') }}
      schema: STAGING
      threads: 4
"""
    
    with open(dest_file, 'w') as f:
        f.write(profiles_content)
    
    print(f"✅ Created dbt profiles.yml at {dest_file}")

if __name__ == "__main__":
    setup_dbt_profiles()
