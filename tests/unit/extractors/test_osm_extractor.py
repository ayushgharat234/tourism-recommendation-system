import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.extractors.osm_extractor import OSMExtractor

class TestOSMExtractor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.extractor = OSMExtractor()
        
    def test_get_tourism_query(self):
        """Test if the tourism query is correctly formatted."""
        query = self.extractor.get_tourism_query()
        self.assertIsInstance(query, str)
        self.assertIn('area["name"="India"]', query)
        self.assertIn('tourism', query)

    @patch('src.extractors.osm_extractor.Overpass')  # ✅ Correctly patched
    def test_extract_locations(self, mock_overpass):
        """Test location extraction with mocked Overpass API."""
        # Mock API response
        mock_api = MagicMock()
        mock_node = MagicMock()
        mock_node.id = 1234
        mock_node.lat = "27.1751"
        mock_node.lon = "78.0421"
        mock_node.tags = {
            "name": "Taj Mahal",
            "tourism": "monument",
            "historic": "yes"
        }

        # Ensure only one node is in the response
        mock_api.query.return_value.nodes = [mock_node]
        mock_api.query.return_value.ways = []

        # Return mock API response when Overpass is called
        mock_overpass.return_value = mock_api

        # Test extraction
        locations = self.extractor.extract_locations()

        # Ensure that the returned locations list has exactly 1 location
        self.assertIsInstance(locations, list)
        self.assertEqual(len(locations), 1)

    def test_create_dataframe(self):
        """Test conversion of locations to DataFrame."""
        test_locations = [{
            'osm_id': 1234,
            'name': 'Taj Mahal',
            'type': 'node',
            'lat': 27.1751,
            'lon': 78.0421,
            'tourism_type': 'monument',
            'tags': {
                'name': 'Taj Mahal',
                'tourism': 'monument'
            }
        }]

        df = self.extractor.create_dataframe(test_locations)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['osm_id'], 1234)
        self.assertEqual(df.iloc[0]['name'], 'Taj Mahal')

if __name__ == '__main__':
    unittest.main()