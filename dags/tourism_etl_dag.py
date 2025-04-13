from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Import our plugin modules
from tourism.extractors.osm_extractor import OSMExtractor
from tourism.extractors.ai_generator import AIContentGenerator
from tourism.transformers.data_transformer import DataTransformer
from tourism.loaders.db_loader import DatabaseLoader

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def extract_osm_data(**context):
    """Extract tourism data from OpenStreetMap."""
    extractor = OSMExtractor()
    locations = extractor.extract_locations()
    context['task_instance'].xcom_push(key='locations', value=locations)
    return "Extracted {} locations".format(len(locations))

def generate_ai_content(**context):
    """Generate AI-enhanced content for locations."""
    locations = context['task_instance'].xcom_pull(key='locations', task_ids='extract_osm_data')
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
    
    context['task_instance'].xcom_push(key='enhanced_data', value=enhanced_data)
    return "Generated content for {} locations".format(len(enhanced_data))

def transform_data(**context):
    """Transform and clean the data."""
    enhanced_data = context['task_instance'].xcom_pull(key='enhanced_data', task_ids='generate_ai_content')
    transformer = DataTransformer()
    
    # Transform locations data
    locations_data = [item['location'] for item in enhanced_data]
    locations_df = transformer.clean_locations_data(pd.DataFrame(locations_data))
    
    # Transform AI-generated content
    descriptions_df, interactions_df = transformer.process_ai_content(enhanced_data)
    
    # Store transformed data
    context['task_instance'].xcom_push(key='locations_df', value=locations_df.to_dict())
    context['task_instance'].xcom_push(key='descriptions_df', value=descriptions_df.to_dict())
    context['task_instance'].xcom_push(key='interactions_df', value=interactions_df.to_dict())
    
    return "Transformed data successfully"

def load_data(**context):
    """Load data into PostgreSQL database."""
    loader = DatabaseLoader()
    
    # Get transformed data
    locations_df = pd.DataFrame(context['task_instance'].xcom_pull(key='locations_df', task_ids='transform_data'))
    descriptions_df = pd.DataFrame(context['task_instance'].xcom_pull(key='descriptions_df', task_ids='transform_data'))
    interactions_df = pd.DataFrame(context['task_instance'].xcom_pull(key='interactions_df', task_ids='transform_data'))
    
    # Load data
    loader.load_locations(locations_df)
    loader.load_descriptions(descriptions_df)
    loader.load_interactions(interactions_df)
    
    return "Data loaded successfully"

# Create DAG
dag = DAG(
    'tourism_etl',
    default_args=default_args,
    description='ETL pipeline for tourism data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['tourism']
)

# Create tasks
with open('/opt/airflow/sql/init.sql', 'r') as f:
    sql_content = f.read()

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

# Set task dependencies
create_tables >> extract_data >> generate_content >> transform >> load 