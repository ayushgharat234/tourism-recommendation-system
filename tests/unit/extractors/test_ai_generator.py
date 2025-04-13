import unittest
from unittest.mock import patch, MagicMock
import os
from src.extractors.ai_generator import AIContentGenerator

class TestAIContentGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock environment variable
        os.environ['OPENAI_API_KEY'] = 'test_key'
        self.generator = AIContentGenerator()
        
        self.test_location = {
            'osm_id': 1234,
            'name': 'Taj Mahal',
            'type': 'monument',
            'tourism_type': 'historic',
            'addr_city': 'Agra',
            'addr_state': 'Uttar Pradesh'
        }
        
    @patch('openai.ChatCompletion.create')
    def test_generate_enhanced_description(self, mock_openai):
        """Test generation of enhanced descriptions."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"description": "The Taj Mahal is a stunning ivory-white marble mausoleum.", "best_time": "October to March", "cultural_significance": "Symbol of eternal love", "key_attractions": "Main mausoleum, gardens, mosque", "travel_tips": "Visit early morning to avoid crowds"}'
                )
            )
        ]
        mock_openai.return_value = mock_response
        
        result = self.generator.generate_enhanced_description(self.test_location)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['location_id'], 1234)
        self.assertIn('description', result)
        self.assertIn('best_time', result)
        self.assertIn('cultural_significance', result)
        self.assertIn('key_attractions', result)
        self.assertIn('travel_tips', result)
        
    @patch('openai.ChatCompletion.create')
    def test_generate_interaction_data(self, mock_openai):
        """Test generation of interaction data."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"avg_rating": 4.8, "review_count": 1000, "common_activities": "Photography, guided tours", "typical_duration": "2-3 hours", "peak_hours": "9 AM to 11 AM"}'
                )
            )
        ]
        mock_openai.return_value = mock_response
        
        result = self.generator.generate_interaction_data(self.test_location)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['location_id'], 1234)
        self.assertIsInstance(result['avg_rating'], float)
        self.assertIsInstance(result['review_count'], int)
        self.assertIn('common_activities', result)
        self.assertIn('typical_duration', result)
        self.assertIn('peak_hours', result)
        
    def test_missing_api_key(self):
        """Test handling of missing API key."""
        os.environ.pop('OPENAI_API_KEY', None)
        with self.assertRaises(ValueError):
            AIContentGenerator()
            
if __name__ == '__main__':
    unittest.main() 