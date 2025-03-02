import os

# Database: for demo purposes we use SQLite; in production, use PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# API key for authentication (in production, manage secrets securely)
API_KEY = os.getenv("API_KEY", "mysecretapikey")

# For testing without Redis, use SQLite as broker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "sqla+sqlite:///celery.sqlite")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "db+sqlite:///celery-results.sqlite")

# AI Model API Keys (in production, manage these securely)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Check if API keys are set
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set. OpenAI API calls will fail.")
if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY is not set. Anthropic API calls will fail.")
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY is not set. Google API calls will fail.")
