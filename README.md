# Movie Location API

API REST construida con FastAPI para gestionar locaciones de filmación de películas. Permite catalogar películas, registrar locaciones geográficas y asociarlas entre sí con descripciones de escenas.

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **SQLite** — base de datos
- **Pydantic** — validación de datos
- **Uvicorn** — servidor ASGI
- **python-dotenv** — configuración por variables de entorno

## Instalación

```bash
# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=sqlite:///./movie_locations.db
```

## Uso

```bash
# Iniciar servidor de desarrollo
uvicorn app.main:app --reload

# Con host y puerto explícitos
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
# Poblar la base de datos con datos de ejemplo
python seed.py
```

La API queda disponible en `http://localhost:8000`.
Documentación interactiva (Swagger UI): `http://localhost:8000/docs`
Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

## Estructura del proyecto

```
movie_location/
├── app/
│   ├── routers/
│   │   ├── movies.py
│   │   ├── locations.py
│   │   └── movie_locations.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── config.py
├── seed.py
├── requirements.txt
└── .env
```

## Modelos

### Movie

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `title` | String | Título único |
| `year` | Integer | Año de estreno |
| `director` | String | Director |
| `genre` | String | Género |
| `imdb_id` | String | ID de IMDb (opcional) |
| `created_at` | DateTime | Fecha de creación |

### Location

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `name` | String | Nombre de la locación |
| `location_type` | String | `exterior` / `interior` / `mixto` |
| `city` | String | Ciudad |
| `country` | String | País |
| `latitude` | Float | Latitud (opcional) |
| `longitude` | Float | Longitud (opcional) |
| `description` | String | Descripción (opcional) |
| `created_at` | DateTime | Fecha de creación |

### MovieLocation

Tabla de asociación entre películas y locaciones.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `movie_id` | Integer | FK a movies |
| `location_id` | Integer | FK a locations |
| `scene_description` | String | Descripción de la escena (opcional) |
| `notes` | Text | Notas adicionales (opcional) |
| `created_at` | DateTime | Fecha de creación |

> La combinación `(movie_id, location_id)` es única.

## Endpoints

### Películas — `/movies`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/movies/` | Listar películas (filtros: `genre`, `skip`, `limit`) |
| `POST` | `/movies/` | Crear película |
| `GET` | `/movies/{movie_id}` | Obtener película por ID |
| `PUT` | `/movies/{movie_id}` | Actualizar película |
| `DELETE` | `/movies/{movie_id}` | Eliminar película |

### Locaciones — `/locations`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/locations/` | Listar locaciones (filtros: `city`, `country`, `skip`, `limit`) |
| `POST` | `/locations/` | Crear locación |
| `GET` | `/locations/{location_id}` | Obtener locación por ID |
| `PUT` | `/locations/{location_id}` | Actualizar locación |
| `DELETE` | `/locations/{location_id}` | Eliminar locación |

### Asociaciones — `/movie-locations`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/movie-locations/` | Listar asociaciones (`skip`, `limit`) |
| `POST` | `/movie-locations/` | Crear asociación |
| `DELETE` | `/movie-locations/{movie_location_id}` | Eliminar asociación |
