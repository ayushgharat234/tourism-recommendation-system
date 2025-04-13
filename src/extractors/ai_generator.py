import os
import openai
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from src.utils.logger import ai_logger

load_dotenv()

class AIContentGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            ai_logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found in environment variables")
            
    def generate_enhanced_description(self, location_data: Dict) -> Optional[Dict]:
        """Generate enhanced descriptions and metadata for a location using AI."""
        try:
            name = location_data.get('name', '')
            original_desc = location_data.get('description', '')
            location_type = location_data.get('tourism_type', '')
            city = location_data.get('addr_city', '')
            state = location_data.get('addr_state', '')
            
            ai_logger.info(f"Generating enhanced description for {name} in {city}, {state}")
            
            prompt = f"""Generate a detailed tourist description for {name} in {city}, {state}, India.
            Type: {location_type}
            Original description: {original_desc}
            
            Please provide:
            1. A compelling description
            2. Best time to visit
            3. Cultural significance
            4. Key attractions
            5. Travel tips
            
            Format as JSON with these keys: description, best_time, cultural_significance, key_attractions, travel_tips"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable travel expert specializing in Indian tourism."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the JSON response
            ai_content = json.loads(response.choices[0].message.content)
            ai_content['location_id'] = location_data.get('osm_id')
            ai_logger.info(f"Successfully generated description for {name}")
            return ai_content
            
        except Exception as e:
            ai_logger.error(f"Error generating AI content for {location_data.get('name', 'unknown location')}: {str(e)}")
            return None
            
    def generate_interaction_data(self, location_data: Dict) -> Optional[Dict]:
        """Generate simulated user interaction data for a location."""
        try:
            name = location_data.get('name', '')
            location_type = location_data.get('tourism_type', '')
            
            ai_logger.info(f"Generating interaction data for {name} ({location_type})")
            
            prompt = f"""Generate simulated user interaction data for {name} ({location_type}) in India.
            Include:
            1. Average rating (1-5)
            2. Number of reviews
            3. Common activities
            4. Typical visit duration
            5. Peak visiting hours
            
            Format as JSON with these keys: avg_rating, review_count, common_activities, typical_duration, peak_hours"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analyst specializing in tourism patterns."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            interaction_data = json.loads(response.choices[0].message.content)
            interaction_data['location_id'] = location_data.get('osm_id')
            ai_logger.info(f"Successfully generated interaction data for {name}")
            return interaction_data
            
        except Exception as e:
            ai_logger.error(f"Error generating interaction data for {location_data.get('name', 'unknown location')}: {str(e)}")
            return None 