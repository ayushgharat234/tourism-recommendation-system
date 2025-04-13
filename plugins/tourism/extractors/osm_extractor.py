import overpy
import pandas as pd
from typing import List, Dict
import logging
import os
from dotenv import load_dotenv

load_dotenv()

class OSMExtractor:
    def __init__(self):
        self.api = overpy.Overpass()
        self.timeout = int(os.getenv('OSM_TIMEOUT', 300))
        self.area = os.getenv('OSM_AREA', 'India')
        
    def get_tourism_query(self) -> str:
        """Generate Overpass QL query for tourism locations in India."""
        return f"""
        [out:json][timeout:{self.timeout}];
        area[name="{self.area}"]->.searchArea;
        (
          node["tourism"](area.searchArea);
          way["tourism"](area.searchArea);
          relation["tourism"](area.searchArea);
          
          node["historic"](area.searchArea);
          way["historic"](area.searchArea);
          relation["historic"](area.searchArea);
          
          node["leisure"="park"](area.searchArea);
          way["leisure"="park"](area.searchArea);
          
          node["natural"="beach"](area.searchArea);
          way["natural"="beach"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
    def extract_locations(self) -> List[Dict]:
        """Extract tourism locations from OpenStreetMap."""
        try:
            logging.info("Starting extraction of tourism locations from OSM")
            result = self.api.query(self.get_tourism_query())
            locations = []
            
            # Process nodes (points)
            for node in result.nodes:
                location = {
                    'osm_id': node.id,
                    'type': 'node',
                    'lat': float(node.lat),
                    'lon': float(node.lon),
                    'tags': dict(node.tags),
                    'name': node.tags.get('name', ''),
                    'tourism_type': node.tags.get('tourism',
                                               node.tags.get('historic',
                                                           node.tags.get('leisure',
                                                                       node.tags.get('natural', ''))))
                }
                locations.append(location)
                
            # Process ways (areas/buildings)
            for way in result.ways:
                if len(way.nodes) > 0:
                    # Calculate centroid for ways
                    lat = sum(float(node.lat) for node in way.nodes) / len(way.nodes)
                    lon = sum(float(node.lon) for node in way.nodes) / len(way.nodes)
                    
                    location = {
                        'osm_id': way.id,
                        'type': 'way',
                        'lat': lat,
                        'lon': lon,
                        'tags': dict(way.tags),
                        'name': way.tags.get('name', ''),
                        'tourism_type': way.tags.get('tourism',
                                                   way.tags.get('historic',
                                                               way.tags.get('leisure',
                                                                           way.tags.get('natural', ''))))
                    }
                    locations.append(location)
            
            logging.info(f"Extracted {len(locations)} locations from OSM")
            return locations
            
        except Exception as e:
            logging.error(f"Error extracting locations: {str(e)}")
            return []
    
    def create_dataframe(self, locations: List[Dict]) -> pd.DataFrame:
        """Convert locations to a pandas DataFrame."""
 