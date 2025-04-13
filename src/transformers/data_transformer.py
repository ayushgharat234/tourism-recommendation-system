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
            string_columns = ['name', 'tourism_type', 'description', 'website', 'phone']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('').str.strip()
                    
            # Ensure numeric columns are correct type
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            
            # Remove rows with invalid coordinates
            df = df[
                (df['lat'].between(8.4, 37.6)) &  # India's latitude range
                (df['lon'].between(68.7, 97.25))   # India's longitude range
            ]
            
            return df
            
        except Exception as e:
            logging.error(f"Error cleaning locations data: {str(e)}")
            raise
            
    def process_ai_content(self, ai_contents: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process AI-generated content into descriptions and interactions DataFrames."""
        try:
            # Process descriptions
            descriptions = []
            for content in ai_contents:
                if not content:
                    continue
                    
                desc_data = {
                    'location_id': content.get('location_id'),
                    'description': content.get('description', ''),
                    'best_time': content.get('best_time', ''),
                    'cultural_significance': content.get('cultural_significance', ''),
                    'key_attractions': content.get('key_attractions', ''),
                    'travel_tips': content.get('travel_tips', '')
                }
                descriptions.append(desc_data)
                
            # Process interactions
            interactions = []
            for content in ai_contents:
                if not content:
                    continue
                    
                interaction_data = {
                    'location_id': content.get('location_id'),
                    'avg_rating': content.get('avg_rating', 0.0),
                    'review_count': content.get('review_count', 0),
                    'common_activities': content.get('common_activities', ''),
                    'typical_duration': content.get('typical_duration', ''),
                    'peak_hours': content.get('peak_hours', '')
                }
                interactions.append(interaction_data)
                
            desc_df = pd.DataFrame(descriptions)
            inter_df = pd.DataFrame(interactions)
            
            # Clean and validate
            if not desc_df.empty:
                desc_df = desc_df.dropna(subset=['location_id'])
            if not inter_df.empty:
                inter_df = inter_df.dropna(subset=['location_id'])
                inter_df['avg_rating'] = pd.to_numeric(inter_df['avg_rating'], errors='coerce')
                inter_df['review_count'] = pd.to_numeric(inter_df['review_count'], errors='coerce')
                
            return desc_df, inter_df
            
        except Exception as e:
            logging.error(f"Error processing AI content: {str(e)}")
            raise 