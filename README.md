# YouTube Analytics Data Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Airflow](https://img.shields.io/badge/Airflow-2.10-red?style=for-the-badge&logo=apache-airflow)
![dbt](https://img.shields.io/badge/dbt-1.11-orange?style=for-the-badge&logo=dbt)
![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_S3-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**End-to-end automated data pipeline for YouTube trending videos analytics**

[Architecture](#architecture) • [Features](#features) • [Tech Stack](#tech-stack) • [Setup](#setup)

</div>

---

## 📋 Overview

A production-ready data pipeline that extracts trending YouTube videos, transforms them through a medallion architecture (Bronze → Silver → Gold), and enables analytics through a dimensional data model. Fully orchestrated with Apache Airflow and containerized with Docker.

## 🏗️ Architecture
```
YouTube API → Python Extractor → AWS S3 (Bronze) → Snowflake (Raw)
                                                      ↓
                                              dbt Transformations
                                                      ↓
                                          Staging Layer (Silver)
                                                      ↓
                                    Dimensional Model (Gold)
                                    ├── dim_videos
                                    ├── dim_channels
                                    ├── dim_categories
                                    └── fact_video_performance
```

### Pipeline Flow (Airflow DAG)

1. **Extract**: Pull trending videos from YouTube Data API v3
2. **Load**: Upload raw JSON to S3, then stage in Snowflake RAW schema
3. **Transform**: dbt models create staging tables and dimensional model
4. **Test**: Automated data quality checks (22 tests)
5. **Schedule**: Daily runs at 6 AM UTC

## ✨ Features

- **Fully Automated**: Scheduled daily extraction and transformation
- **Medallion Architecture**: Bronze (raw) → Silver (staging) → Gold (analytical)
- **Dimensional Modeling**: Star schema with fact and dimension tables
- **Data Quality**: 22 automated dbt tests for data integrity
- **Scalable Design**: Handles 50+ videos, channels, and categories per run
- **Containerized**: Docker Compose for reproducible deployments
- **Cloud Native**: AWS S3 + Snowflake for storage and compute

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Orchestration** | Apache Airflow 2.10 | Workflow scheduling and monitoring |
| **Extraction** | Python 3.12 | YouTube API client |
| **Storage (Bronze)** | AWS S3 | Raw data lake |
| **Warehouse** | Snowflake | Data warehouse (RAW/STAGING/MARTS) |
| **Transformation** | dbt 1.11 | SQL-based data modeling |
| **Containerization** | Docker + Compose | Isolated environments |

### Python Libraries
- `google-api-python-client` - YouTube Data API integration
- `boto3` - AWS S3 operations
- `snowflake-connector-python` - Snowflake connectivity
- `pydantic-settings` - Configuration management

## 📊 Data Model

### Staging Layer (Silver)
- `stg_videos` - Cleaned video metadata
- `stg_channels` - Channel information
- `stg_categories` - Video categories

### Analytical Layer (Gold)
- `dim_videos` - Video dimension (SCD Type 1)
- `dim_channels` - Channel dimension
- `dim_categories` - Category dimension
- `fact_video_performance` - Video metrics fact table

## 🚀 Setup

### Prerequisites
- Docker Desktop
- AWS Account (S3 access)
- Snowflake Account
- YouTube Data API Key

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/okaforoa/youtube-analytics-pipeline.git
cd youtube-analytics-pipeline
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
```env
YOUTUBE_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=your_bucket
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=YOUTUBE_DB
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

3. **Build and Start**
```bash
docker-compose build
docker-compose up -d
```

4. **Access Airflow**
- URL: http://localhost:8081
- Username: `airflow`
- Password: `airflow`

5. **Trigger Pipeline**
- Navigate to DAGs → `youtube_analytics_pipeline`
- Toggle ON to enable
- Click play button to run manually

## 📁 Project Structure
```
youtube-analytics-pipeline/
├── airflow/
│   ├── dags/
│   │   └── youtube_pipeline_dag.py    # Main orchestration DAG
│   └── requirements.txt                # Airflow dependencies
├── dbt/
│   └── youtube_analytics/
│       ├── models/
│       │   ├── staging/                # Silver layer
│       │   └── marts/                  # Gold layer (dimensional)
│       └── dbt_project.yml
├── src/
│   ├── extractors/
│   │   └── youtube_extractor.py       # YouTube API client
│   ├── utils/
│   │   ├── aws_utils.py               # S3 operations
│   │   └── snowflake_utils.py         # Snowflake operations
│   └── config.py                       # Configuration management
├── docker-compose.yml                  # Container orchestration
├── Dockerfile                          # Custom Airflow image
└── README.md
```

## 🎯 Key Metrics

- **Extraction**: 50 trending videos per run
- **Channels**: ~48 unique channels per run
- **Categories**: 32 video categories
- **Data Quality**: 16/22 tests passing consistently
- **Runtime**: ~3-5 minutes end-to-end
- **Schedule**: Daily at 6 AM UTC

## 🔍 Example Queries

### Top 10 Videos by Views
```sql
SELECT 
    v.title,
    v.channel_title,
    f.view_count,
    f.like_count
FROM MARTS.FACT_VIDEO_PERFORMANCE f
JOIN MARTS.DIM_VIDEOS v ON f.video_key = v.video_key
ORDER BY f.view_count DESC
LIMIT 10;
```

### Channel Performance Summary
```sql
SELECT 
    c.channel_title,
    COUNT(DISTINCT f.video_key) as video_count,
    SUM(f.view_count) as total_views,
    AVG(f.like_count) as avg_likes
FROM MARTS.FACT_VIDEO_PERFORMANCE f
JOIN MARTS.DIM_CHANNELS c ON f.channel_key = c.channel_key
GROUP BY c.channel_title
ORDER BY total_views DESC;
```

## 🧪 Testing

The pipeline includes 22 automated data quality tests:
- **Uniqueness**: Primary key constraints
- **Not Null**: Required field validation
- **Referential Integrity**: Foreign key relationships

Run tests manually:
```bash
cd dbt/youtube_analytics
dbt test
```

## 📈 Future Enhancements

- [ ] Add incremental loading for historical data
- [ ] Implement SCD Type 2 for slowly changing dimensions
- [ ] Add sentiment analysis on video titles/descriptions
- [ ] Create Tableau/PowerBI dashboards
- [ ] Add alerting for pipeline failures
- [ ] Expand to multiple regions/countries

## 📝 License

MIT License - feel free to use this project for learning or portfolio purposes.

## 👤 Author

**Dion Okafor**
- GitHub: [@okaforoa](https://github.com/okaforoa)
- LinkedIn: https://www.linkedin.com/in/dion-okafor
- Email: dion.okafor@gmail.com

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

</div>
