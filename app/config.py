from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./movie_locations.db")

# Keys válidas para endpoints de escritura, separadas por coma (permite una key por cliente y rotar sin downtime)
API_KEYS = {k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()}
