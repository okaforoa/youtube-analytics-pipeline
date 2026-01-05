# YouTube Analytics Data Pipeline

An end-to-end data engineering project that extracts trending video data from the YouTube Data API, processes it through a medallion architecture (Bronze → Silver → Gold), and creates analytics-ready datasets for insights.

## Architecture
```
YouTube API → Python → AWS S3 (Bronze) → Snowflake → dbt (Silver/Gold) → Orchestrated by Airflow
```

## Tech Stack

- **Orchestration**: Apache Airflow
- **Data Warehouse**: Snowflake
- **Transformation**: dbt Core
- **Storage**: AWS S3
- **Language**: Python 3.11+
- **Containerization**: Docker & Docker Compose
- **Data Quality**: Soda Core + dbt tests
- **CI/CD**: GitHub Actions

## Project Structure
```
youtube-data-pipeline/
├── airflow/           # Airflow DAGs and configuration
├── dbt/              # dbt models and tests
├── src/              # Python source code
├── tests/            # Unit tests
├── soda/             # Data quality checks
└── .github/          # CI/CD workflows
```

## Data Sources

- YouTube trending videos by region
- Video statistics (views, likes, comments, shares)
- Channel information and subscriber counts
- Video metadata (category, tags, duration)
- Engagement metrics and ratios

## Analytics Use Cases

- Track trending content patterns over time
- Analyze engagement rates (likes/views, comments/views)
- Compare regional differences in content popularity
- Monitor channel growth and performance
- Identify successful video characteristics

## Development Status

- [x] Project structure setup
- [x] Configuration management
- [x] AWS S3 integration
- [x] Snowflake connection
- [x] YouTube data extraction
- [x] Bronze layer ingestion
- [x] dbt transformations (Silver/Gold)
- [ ] Airflow orchestration
- [ ] Data quality checks

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- AWS Account
- Snowflake Account
- Google Cloud Account (for YouTube Data API)

### Installation
```bash
# Clone repository
git clone https://github.com/okaforoa/spotify-data-pipeline.git
cd spotify-data-pipeline

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install -r requirements.txt
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - YouTube API Key
# - AWS credentials
# - Snowflake credentials
```

## Data Model

### Bronze Layer
- Raw JSON responses from YouTube API

### Silver Layer
- Cleaned and validated video data
- Normalized channel information
- Staging tables with data quality tests

### Gold Layer
- Dimensional model (star schema)
- `fact_video_performance`
- `dim_videos`
- `dim_channels`
- `dim_categories`
- `dim_dates`

## License

MIT
