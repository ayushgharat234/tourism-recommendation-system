from datetime import datetime, timedelta
import pandas as pd
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Ensure custom module path is available
dag_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(dag_folder, '..')  # adjust if needed
sys.path.append(project_root)

# Import custom modules
from src.extractors.osm_extractor import OSMExtractor
from src.extractors.ai_generator import AIContentGenerator
from src.transformers.data_transformer import DataTransformer
from src.loaders.db_loader import DatabaseLoader

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Task 1: Extract OSM data
def extract_osm_data(**context):
    extractor = OSMExtractor()
    locations = extractor.extract_locations()
    context['ti'].xcom_push(key='locations', value=locations)
    return f"Extracted {len(locations)} locations"

# Task 2: Generate AI content
def generate_ai_content(**context):
    locations = context['ti'].xcom_pull(key='locations', task_ids='extract_osm_data')
    generator = AIContentGenerator()
    enhanced_data = []

    for location in locations:
        description = generator.generate_enhanced_description(location)
        interaction = generator.generate_interaction_data(location)
        if description and interaction:
            enhanced_data.append({
                'location': location,
                'description': description,
                'interaction': interaction
            })

    context['ti'].xcom_push(key='enhanced_data', value=enhanced_data)
    return f"Generated content for {len(enhanced_data)} locations"

# Task 3: Transform data
def transform_data(**context):
    enhanced_data = context['ti'].xcom_pull(key='enhanced_data', task_ids='generate_ai_content')
    transformer = DataTransformer()

    # Clean location data
    locations_data = [item['location'] for item in enhanced_data]
    locations_df = transformer.clean_locations_data(pd.DataFrame(locations_data))

    # Flatten for AI processing
    flattened = []
    for item in enhanced_data:
        location = item.get("location", {})
        description = item.get("description", {})
        interaction = item.get("interaction", {})

        flattened.append({
            "location_id": location.get("osm_id"),
            "description": description.get("text", ""),
            "tags": location.get("tags", ""),
            "best_time": description.get("best_time", ""),
            "cultural_significance": description.get("cultural_significance", ""),
            "key_attractions": description.get("key_attractions", ""),
            "travel_tips": description.get("travel_tips", ""),
            "avg_rating": interaction.get("avg_rating", 0.0),
            "review_count": interaction.get("review_count", 0),
            "common_activities": interaction.get("common_activities", ""),
            "typical_duration": interaction.get("typical_duration", ""),
            "peak_hours": interaction.get("peak_hours", "")
        })

    desc_df, inter_df = transformer.process_ai_content(flattened)

    context['ti'].xcom_push(key='locations_df', value=locations_df.to_json())
    context['ti'].xcom_push(key='descriptions_df', value=desc_df.to_json())
    context['ti'].xcom_push(key='interactions_df', value=inter_df.to_json())
    return f"Transformed {len(flattened)} records"

# Task 4: Load data
def load_data(**context):
    loader = DatabaseLoader()

    locations_df = pd.read_json(context['ti'].xcom_pull(key='locations_df', task_ids='transform_data'))
    descriptions_df = pd.read_json(context['ti'].xcom_pull(key='descriptions_df', task_ids='transform_data'))
    interactions_df = pd.read_json(context['ti'].xcom_pull(key='interactions_df', task_ids='transform_data'))

    loader.load_locations(locations_df)
    loader.load_descriptions(descriptions_df)
    loader.load_interactions(interactions_df)
    return "Data loaded successfully"

# DAG definition
dag = DAG(
    'tourism_etl',
    default_args=default_args,
    description='ETL pipeline for tourism data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['tourism']
)

# SQL init schema loading (safe)
sql_path = os.path.join(project_root, 'sql', 'init.sql')
if not os.path.exists(sql_path):
    raise FileNotFoundError(f"SQL init file not found: {sql_path}")
with open(sql_path, 'r') as f:
    sql_content = f.read()

# Define tasks
create_tables = PostgresOperator(
    task_id='create_tables',
    postgres_conn_id='postgres_default',
    sql=sql_content,
    dag=dag
)

extract_data = PythonOperator(
    task_id='extract_osm_data',
    python_callable=extract_osm_data,
    provide_context=True,
    dag=dag
)

generate_content = PythonOperator(
    task_id='generate_ai_content',
    python_callable=generate_ai_content,
    provide_context=True,
    dag=dag
)

transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)

load = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag
)

# DAG Task flow
create_tables >> extract_data >> generate_content >> transform >> load