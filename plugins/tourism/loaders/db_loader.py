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
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'airflow')
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
            
    def load_locations(self, df: pd.DataFrame):
        """Load locations data into the database."""
        try:
            logging.info(f"Loading {len(df)} locations into database")
            df.to_sql('locations', self.engine, if_exists='append', index=False)
            logging.info("Successfully loaded locations data")
        except SQLAlchemyError as e:
            logging.error(f"Error loading locations data: {str(e)}")
            raise
            
    def load_descriptions(self, df: pd.DataFrame):
        """Load descriptions data into the database."""
        try:
            logging.info(f"Loading {len(df)} descriptions into database")
            df.to_sql('descriptions', self.engine, if_exists='append', index=False)
            logging.info("Successfully loaded descriptions data")
        except SQLAlchemyError as e:
            logging.error(f"Error loading descriptions data: {str(e)}")
            raise
            
    def load_interactions(self, df: pd.DataFrame):
        """Load interactions data into the database."""
        try:
            logging.info(f"Loading {len(df)} interactions into database")
            df.to_sql('interactions', self.engine, if_exists='append', index=False)
            logging.info("Successfully loaded interactions data")
        except SQLAlchemyError as e:
            logging.error(f"Error loading interactions data: {str(e)}")
            raise 