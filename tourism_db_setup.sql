-- First, create extensions for spatial queries
CREATE EXTENSION IF NOT EXISTS cube;
CREATE EXTENSION IF NOT EXISTS earthdistance;

-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
    osm_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    tourism_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index for coordinates
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations USING gist (ll_to_earth(lat, lon));
CREATE INDEX IF NOT EXISTS idx_locations_tourism_type ON locations(tourism_type);

-- Create descriptions table
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

CREATE INDEX IF NOT EXISTS idx_descriptions_location ON descriptions(location_id);

-- Create interactions table
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

CREATE INDEX IF NOT EXISTS idx_interactions_location ON interactions(location_id);
CREATE INDEX IF NOT EXISTS idx_interactions_rating ON interactions(avg_rating);

-- Grant permissions to airflow user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO airflow; 