from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./movie_locations.db")

# Keys válidas para endpoints de escritura, separadas por coma (permite una key por cliente y rotar sin downtime)
API_KEYS = {k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()}

# Tope de requests por IP, formato de `limits` (ej. "120/minute", "10/second")
RATE_LIMIT = os.getenv("RATE_LIMIT", "120/minute")
