from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./movie_locations.db")

# Keys válidas para endpoints de escritura, separadas por coma (permite una key por cliente y rotar sin downtime)
API_KEYS = {k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()}

# Máximo de items por página en los listados
MAX_PAGE_SIZE = 500

# Máximo de películas por request en POST /import/movies
MAX_IMPORT_BATCH = 200

# Tope de requests por IP, formato de `limits` (ej. "120/minute", "10/second")
RATE_LIMIT = os.getenv("RATE_LIMIT", "120/minute")
