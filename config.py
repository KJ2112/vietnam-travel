# config.py
# Configuration file for API keys and environment variables

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_2jDwk5_9XMg83yEqpMQbfaH4NHbFJpon9MvFy7rwuJdtWiyWBqJCGD489HULhmQaSKbpip")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "vietnam-travel-768")

# Ollama Configuration (for embeddings only)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

# Gemini Configuration (for chat)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD10yKJ06yWaQxA6yb_E-iyGnJ465j5Qog")  # Set this in your .env file
GEMINI_CHAT_MODEL = "gemini-2.5-flash"  # Fast and free

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://cb139e65.databases.neo4j.io")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "9gaEoOCTJTcld340QjbaOCJ-xLIULZ7xxjBH_MJgNdI")

# Application Settings
EMBEDDING_DIMENSION = 768  # nomic-embed-text has 768 dimensions
TOP_K_RESULTS = 5
BATCH_SIZE = 100

# Validation
def validate_config():
    """Validate that all required configuration is present"""
    required_vars = {
        "PINECONE_API_KEY": PINECONE_API_KEY,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "NEO4J_PASSWORD": NEO4J_PASSWORD
    }
    
    missing = [k for k, v in required_vars.items() if not v or v.startswith("your_")]
    
    if missing:
        print(f"⚠️  Warning: Missing configuration for: {', '.join(missing)}")
        print("Please update config.py or set environment variables")
        return False
    
    # Test Ollama connection for embeddings only
    try:
        import requests
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if any('nomic-embed' in m.get('name', '') for m in models):
                print("✅ Ollama connection successful")
                print("✅ Nomic embedding model available")
            else:
                print("❌ Nomic embedding model not found")
                return False
        else:
            print("❌ Ollama connection failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running on localhost:11434")
        return False
    
    # Test Gemini configuration
    if not GEMINI_API_KEY:
        print("❌ Gemini API key not set")
        return False
    else:
        print("✅ Gemini API key configured")
    
    return True

if __name__ == "__main__":
    if validate_config():
        print("✅ Configuration validated successfully!")
    else:
        print("❌ Please configure your API keys before running the application")