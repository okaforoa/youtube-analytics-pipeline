# Spotify Data Pipeline

An end-to-end data engineering project that extracts listening data from the Spotify API, processes it through a medallion architecture (Bronze → Silver → Gold), and creates analytics-ready datasets for insights.

## Architecture
```
Spotify API → Python → AWS S3 (Bronze) → Snowflake → dbt (Silver/Gold) → Orchestrated by Airflow
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
spotify-data-pipeline/
├── airflow/           # Airflow DAGs and configuration
├── dbt/              # dbt models and tests
├── src/              # Python source code
├── tests/            # Unit tests
├── soda/             # Data quality checks
└── .github/          # CI/CD workflows
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- AWS Account
- Snowflake Account (free trial)
- Spotify Developer Account

### 1. Clone and Setup
```bash
git clone <your-repo>
cd spotify-data-pipeline

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### 3. Setup Pre-commit Hooks
```bash
pre-commit install
```

## Development Status

- [x] Project structure setup
- [x] Configuration management
- [x] Virtual environment and dependencies
- [ ] Spotify data extraction
- [ ] AWS S3 integration
- [ ] Snowflake connection
- [ ] dbt models
- [ ] Airflow DAGs
- [ ] Data quality checks
- [ ] CI/CD pipeline

## Data Model

### Bronze Layer
- Raw JSON data from Spotify API

### Silver Layer
- Cleaned, validated, and typed data
- Staging tables with data quality tests

### Gold Layer
- Dimensional model (star schema)
- `fact_listening_events`
- `dim_tracks`
- `dim_artists`
- `dim_dates`

## Monitoring & Quality

- dbt test coverage: 95%+
- Data freshness SLA: < 2 hours
- Automated alerts on pipeline failures

## Future Enhancements

- [ ] Real-time streaming with Kafka
- [ ] ML model for music recommendations
- [ ] Dashboard with Metabase
- [ ] Cost optimization with Snowflake clustering

## License

MIT
