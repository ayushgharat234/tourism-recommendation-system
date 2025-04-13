import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv

load_dotenv()

class DatabaseLoader:
    def __init__(self):
        self.db_params = {
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'tourism_db')
        }
        self.engine = self._create_engine()
        
    def _create_engine(self):
        """Create SQLAlchemy engine with connection parameters."""
        try:
            connection_string = f"postgresql://{self.db_params['user']}:{self.db_params['password']}@{self.db_params['host']}:{self.db_params['port']}/{self.db_params['database']}"
            return create_engine(connection_string)
        except Exception as e:
            logging.error(f"Error creating database engine: {str(e)}")
            raise
            
    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        try:
            # Create locations table
            locations_table = """
            CREATE TABLE IF NOT EXISTS locations (
                osm_id BIGINT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50),
                lat DOUBLE PRECISION,
                lon DOUBLE PRECISION,
                tourism_type VARCHAR(100),
                website VARCHAR(255),
                phone VARCHAR(50),
                addr_city VARCHAR(100),
                addr_state VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Create descriptions table
            descriptions_table = """
            CREATE TABLE IF NOT EXISTS descriptions (
                id SERIAL PRIMARY KEY,
                location_id BIGINT REFERENCES locations(osm_id),
                description TEXT,
                best_time TEXT,
                cultural_significance TEXT,
                key_attractions TEXT,
                travel_tips TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Create interactions table
            interactions_table = """
            CREATE TABLE IF NOT EXISTS interactions (
                id SERIAL PRIMARY KEY,
                location_id BIGINT REFERENCES locations(osm_id),
                avg_rating FLOAT,
                review_count INTEGER,
                common_activities TEXT,
                typical_duration VARCHAR(100),
                peak_hours VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(locations_table))
                conn.execute(text(descriptions_table))
                conn.execute(text(interactions_table))
                conn.commit()
                
        except SQLAlchemyError as e:
            logging.error(f"Error creating database tables: {str(e)}")
            raise
            
    def load_locations(self, df: pd.DataFrame):
        """Load locations data into the database."""
        try:
            df.to_sql('locations', self.engine, if_exists='append', index=False)
        except SQLAlchemyError as e:
            logging.error(f"Error loading locations data: {str(e)}")
            raise
            
    def load_descriptions(self, df: pd.DataFrame):
        """Load descriptions data into the database."""
        try:
            df.to_sql('descriptions', self.engine, if_exists='append', index=False)
        except SQLAlchemyError as e:
            logging.error(f"Error loading descriptions data: {str(e)}")
            raise
            
    def load_interactions(self, df: pd.DataFrame):
        """Load interactions data into the database."""
        try:
            df.to_sql('interactions', self.engine, if_exists='append', index=False)
        except SQLAlchemyError as e:
            logging.error(f"Error loading interactions data: {str(e)}")
            raise 