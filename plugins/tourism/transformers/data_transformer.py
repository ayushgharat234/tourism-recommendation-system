import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

class DataTransformer:
    def __init__(self):
        self.required_columns = [
            'osm_id', 'name', 'type', 'lat', 'lon', 'tourism_type'
        ]
        
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate if the DataFrame has all required columns."""
        return all(col in df.columns for col in self.required_columns)
        
    def clean_locations_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and transform the locations data."""
        if not self.validate_data(df):
            raise ValueError("DataFrame missing required columns")
            
        try:
            # Remove rows with missing essential data
            df = df.dropna(subset=['osm_id', 'name', 'lat', 'lon'])
            
            # Clean string columns
            string_columns = ['name', 'tourism_type', 'description']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('').str.strip()
                    
            # Extract address components from tags
            df['addr_city'] = df['tags'].apply(lambda x: x.get('addr:city', ''))
            df['addr_state'] = df['tags'].apply(lambda x: x.get('addr:state', ''))
            df['website'] = df['tags'].apply(lambda x: x.get('website', ''))
            df['phone'] = df['tags'].apply(lambda x: x.get('phone', ''))
            
            # Ensure numeric columns are correct type
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            
            # Remove rows with invalid coordinates
            df = df[
                (df['lat'].between(8.4, 37.6)) &  # India's latitude range
                (df['lon'].between(68.7, 97.25))   # India's longitude range
            ]
            
            # Drop the tags column as we've extracted what we need
            df = df.drop('tags', axis=1)
            
            return df
            
        except Exception as e:
            logging.error(f"Error cleaning locations data: {str(e)}")
            raise
            
    def process_ai_content(self, ai_contents: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process AI-generated content into descriptions and interactions DataFrames."""
        try:
            descriptions = []
            interactions = []
            
            for item in ai_contents:
                if 'description' in item:
                    desc = item['description']
                    desc['location_id'] = item['location']['osm_id']
                    descriptions.append(desc)
                    
                if 'interaction' in item:
                    inter = item['interaction']
                    inter['location_id'] = item['location']['osm_id']
                    interactions.append(inter)
            
            desc_df = pd.DataFrame(descriptions) if descriptions else pd.DataFrame()
            inter_df = pd.DataFrame(interactions) if interactions else pd.DataFrame()
            
            # Clean up description data
            if not desc_df.empty:
                desc_df = desc_df.dropna(subset=['location_id'])
                
            # Clean up interaction data
            if not inter_df.empty:
                inter_df = inter_df.dropna(subset=['location_id'])
                inter_df['avg_rating'] = pd.to_numeric(inter_df['avg_rating'], errors='coerce')
                inter_df['review_count'] = pd.to_numeric(inter_df['review_count'], errors='coerce')
                
            return desc_df, inter_df
            
        except Exception as e:
            logging.error(f"Error processing AI content: {str(e)}")
            raise 