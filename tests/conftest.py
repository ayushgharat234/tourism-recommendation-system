import os
import sys
import pytest

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def env_setup():
    """Set up environment variables for testing."""
    os.environ['OPENAI_API_KEY'] = 'test_key'
    yield
    # Clean up
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY'] 