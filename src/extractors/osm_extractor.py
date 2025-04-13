import overpy
from overpy import Overpass
import pandas as pd
from typing import List, Dict
import logging

class OSMExtractor:
    def __init__(self):
        self.api = overpy.Overpass()
        
    def get_tourism_query(self) -> str:
        """Generate Overpass QL query for tourism locations in India."""
        return """
        [out:json][timeout:300];
        area["name"="India"]->.india;
        (
          node["tourism"](area.india);
          way["tourism"](area.india);
          relation["tourism"](area.india);
          
          node["historic"](area.india);
          way["historic"](area.india);
          relation["historic"](area.india);
          
          node["leisure"="park"](area.india);
          way["leisure"="park"](area.india);
          
          node["natural"="beach"](area.india);
          way["natural"="beach"](area.india);
        );
        out body;
        >;
        out skel qt;
        """
        
    def extract_locations(self) -> List[Dict]:
        """Extract tourism locations from OpenStreetMap."""
        try:
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
            
            return locations
            
        except Exception as e:
            logging.error(f"Error extracting locations: {str(e)}")
            return []
    
    def create_dataframe(self, locations: List[Dict]) -> pd.DataFrame:
        """Convert locations to a pandas DataFrame."""
        df = pd.DataFrame(locations)
        return df 