"""Configuration management for the YouTube Data Pipeline."""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Get project root and load .env from there
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables from .env file
load_dotenv(dotenv_path=ENV_FILE, override=True)


class YouTubeConfig(BaseSettings):
    """YouTube API configuration."""
    
    api_key: str = Field(default="placeholder", alias="YOUTUBE_API_KEY")
    
    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"


class AWSConfig(BaseSettings):
    """AWS configuration."""
    
    access_key_id: str = Field(..., alias="AWS_ACCESS_KEY_ID")
    secret_access_key: str = Field(..., alias="AWS_SECRET_ACCESS_KEY")
    region: str = Field(default="us-east-2", alias="AWS_REGION")
    bucket_name: str = Field(..., alias="S3_BUCKET_NAME")
    
    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"


class SnowflakeConfig(BaseSettings):
    """Snowflake configuration."""
    
    account: str = Field(..., alias="SNOWFLAKE_ACCOUNT")
    user: str = Field(..., alias="SNOWFLAKE_USER")
    password: str = Field(..., alias="SNOWFLAKE_PASSWORD")
    warehouse: str = Field(default="COMPUTE_WH", alias="SNOWFLAKE_WAREHOUSE")
    database: str = Field(default="YOUTUBE_DB", alias="SNOWFLAKE_DATABASE")
    schema_name: str = Field(default="RAW", alias="SNOWFLAKE_SCHEMA")
    role: str = Field(default="ACCOUNTADMIN", alias="SNOWFLAKE_ROLE")
    
    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"


class AppConfig:
    """Main configuration class."""
    
    def __init__(self):
        print(f"Loading config from: {ENV_FILE}")
        print(f"File exists: {ENV_FILE.exists()}")
        
        self.youtube = YouTubeConfig()
        self.aws = AWSConfig()
        self.snowflake = SnowflakeConfig()
        self.project_root = PROJECT_ROOT


# Global config instance
config = AppConfig()
