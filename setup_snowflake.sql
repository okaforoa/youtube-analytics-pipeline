-- YouTube Analytics Data Pipeline - Snowflake Setup
-- Run this in Snowflake to set up the database structure

-- Create database
CREATE DATABASE IF NOT EXISTS YOUTUBE_DB;
USE DATABASE YOUTUBE_DB;

-- Create schemas for medallion architecture
CREATE SCHEMA IF NOT EXISTS RAW;      -- Bronze layer (raw data from S3)
CREATE SCHEMA IF NOT EXISTS STAGING;  -- Silver layer (cleaned data)
CREATE SCHEMA IF NOT EXISTS ANALYTICS; -- Gold layer (business logic)

-- Create stage for S3 integration
CREATE OR REPLACE STAGE RAW.S3_STAGE
  URL = 's3://youtube-data-pipeline-dion/bronze/'
  CREDENTIALS = (
    AWS_KEY_ID = 'YOUR_AWS_ACCESS_KEY_ID'
    AWS_SECRET_KEY = 'YOUR_AWS_SECRET_ACCESS_KEY'
  );

-- Verify stage was created
SHOW STAGES IN SCHEMA RAW;

-- Create raw tables for YouTube data

-- 1. Trending Videos (raw JSON)
CREATE OR REPLACE TABLE RAW.TRENDING_VIDEOS_RAW (
    FILENAME VARCHAR(500),
    EXTRACTION_TIMESTAMP TIMESTAMP_NTZ,
    REGION VARCHAR(10),
    RAW_DATA VARIANT,
    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 2. Video Categories (raw JSON)
CREATE OR REPLACE TABLE RAW.VIDEO_CATEGORIES_RAW (
    FILENAME VARCHAR(500),
    EXTRACTION_TIMESTAMP TIMESTAMP_NTZ,
    REGION VARCHAR(10),
    RAW_DATA VARIANT,
    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Show created objects
SHOW SCHEMAS IN DATABASE YOUTUBE_DB;
SHOW TABLES IN SCHEMA RAW;

SELECT 'Snowflake setup complete!' AS STATUS;