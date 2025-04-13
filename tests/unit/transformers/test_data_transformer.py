import unittest
import pandas as pd
import numpy as np
from src.transformers.data_transformer import DataTransformer

class TestDataTransformer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.transformer = DataTransformer()
        
        # Create sample test data
        self.test_locations_df = pd.DataFrame({
            'osm_id': [1234, 5678],
            'name': ['Taj Mahal', 'Red Fort'],
            'type': ['monument', 'fort'],
            'lat': [27.1751, 28.6562],
            'lon': [78.0421, 77.2410],
            'tourism_type': ['historic', 'historic'],
            'tags': [
                {'name': 'Taj Mahal', 'tourism': 'monument'},
                {'name': 'Red Fort', 'tourism': 'fort'}
            ]
        })
        
        self.test_ai_content = [
            {
                'location_id': 1234,
                'description': 'Beautiful monument',
                'best_time': 'Morning',
                'cultural_significance': 'Very significant',
                'key_attractions': 'Dome, Gardens',
                'travel_tips': 'Come early',
                'avg_rating': 4.8,
                'review_count': 1000,
                'common_activities': 'Photography',
                'typical_duration': '3 hours',
                'peak_hours': '9 AM - 11 AM'
            }
        ]
        
    def test_validate_data(self):
        """Test data validation."""
        self.assertTrue(self.transformer.validate_data(self.test_locations_df))
        
        # Test with missing columns
        invalid_df = self.test_locations_df.drop('tourism_type', axis=1)
        self.assertFalse(self.transformer.validate_data(invalid_df))
        
    def test_clean_locations_data(self):
        """Test locations data cleaning."""
        cleaned_df = self.transformer.clean_locations_data(self.test_locations_df)
        
        # Check if all required columns exist
        self.assertTrue(all(col in cleaned_df.columns 
                          for col in self.transformer.required_columns))
        
        # Check if numeric columns are correct type
        self.assertTrue(np.issubdtype(cleaned_df['lat'].dtype, np.number))
        self.assertTrue(np.issubdtype(cleaned_df['lon'].dtype, np.number))
        
        # Test invalid coordinates handling
        invalid_df = self.test_locations_df.copy()
        invalid_df.loc[0, 'lat'] = 100  # Invalid latitude
        cleaned_invalid = self.transformer.clean_locations_data(invalid_df)
        self.assertEqual(len(cleaned_invalid), 1)  # Should remove invalid row
        
    def test_process_ai_content(self):
        """Test AI content processing."""
        descriptions_df, interactions_df = self.transformer.process_ai_content(
            self.test_ai_content
        )
        
        # Test descriptions DataFrame
        self.assertIsInstance(descriptions_df, pd.DataFrame)
        self.assertTrue('location_id' in descriptions_df.columns)
        self.assertTrue('description' in descriptions_df.columns)
        self.assertTrue('best_time' in descriptions_df.columns)
        
        # Test interactions DataFrame
        self.assertIsInstance(interactions_df, pd.DataFrame)
        self.assertTrue('location_id' in interactions_df.columns)
        self.assertTrue('avg_rating' in interactions_df.columns)
        self.assertTrue('review_count' in interactions_df.columns)
        
        # Test numeric columns in interactions
        self.assertTrue(np.issubdtype(interactions_df['avg_rating'].dtype, np.number))
        self.assertTrue(np.issubdtype(interactions_df['review_count'].dtype, np.number))
        
if __name__ == '__main__':
    unittest.main() 