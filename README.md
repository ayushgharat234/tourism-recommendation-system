# Indian Tourism Data Pipeline

[![CI/CD](https://github.com/ayushgharat234/tourism-recommendation-system/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ayushgharat234/tourism-recommendation-system/actions/workflows/ci-cd.yml)

An automated ETL pipeline for collecting, processing, and storing Indian tourism data using Apache Airflow.

## Overview

This project implements a data pipeline that:
1. Extracts tourism data from OpenStreetMap for Indian locations
2. Generates AI-enhanced descriptions and interactions for tourist spots
3. Transforms and processes the data
4. Loads it into a PostgreSQL database for use in a recommendation engine

## Components

- **Data Sources**:
  - OpenStreetMap API (primary source for location data)
  - AI-generated content for enhanced descriptions

- **Pipeline Stages**:
  - Extract: Collect raw data from sources
  - Transform: Clean, process, and enhance data
  - Load: Store in PostgreSQL database

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
Create a `.env` file with:
```
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=tourism_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
OPENAI_API_KEY=your_openai_key
```

3. Initialize Airflow:
```bash
airflow db init
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

4. Start Airflow:
```bash
airflow webserver -p 8080
airflow scheduler
```

## Project Structure

```
├── dags/
│   └── tourism_etl_dag.py
├── src/
│   ├── extractors/
│   │   ├── osm_extractor.py
│   │   └── ai_generator.py
│   ├── transformers/
│   │   └── data_transformer.py
│   └── loaders/
│       └── db_loader.py
├── requirements.txt
└── README.md
```

## Data Model

The pipeline creates the following tables in PostgreSQL:
- `locations`: Tourist locations with geographical data
- `descriptions`: Enhanced descriptions and metadata
- `interactions`: User interaction data and ratings

## Contributing

Feel free to contribute by opening issues or submitting pull requests. 