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
API_KEYS=<key1>,<key2>
```

`API_KEYS` es una lista separada por comas de las keys válidas para los endpoints de escritura
(una por cliente permite rotarlas sin downtime). Si no está definida, todas las escrituras
responden `401` (la API falla cerrada). Para generar una key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Uso

```bash
# Iniciar servidor de desarrollo
uvicorn app.main:app --reload

# Con host y puerto explícitos
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
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
│   ├── auth.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── config.py
├── requirements.txt
└── .env
```

## Modelos

### Movie

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `title` | String | Título (no único; la clave natural es `imdb_id`) |
| `year` | Integer | Año de estreno |
| `directors` | list[Director] | Directores (relación muchos-a-muchos) |
| `genres` | list[Genre] | Géneros (relación muchos-a-muchos) |
| `imdb_id` | String | ID de IMDb (único, opcional) |
| `created_at` | DateTime | Fecha de creación |

En `POST`/`PUT` se envían como listas de nombres (`directors: ["Christopher Nolan"]`,
`genres: ["Drama", "Sci-Fi"]`); la API resuelve o crea los registros de `Director`/`Genre`
correspondientes (get-or-create por nombre único).

### Director / Genre

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `name` | String | Nombre único |

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

> `source_text` (interno, no expuesto en la API) guarda el string crudo de `filming_locations`
> del CSV de origen cuando la locación viene del pipeline de `movie_location_data_cl`; es la
> clave natural que usa el loader para hacer upsert sin duplicar ni re-geocodificar.

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

## Autenticación

Las lecturas (`GET`) son públicas. `POST`, `PUT` y `DELETE` requieren el header `X-API-Key`:

```bash
curl -X POST http://localhost:8000/movies/ \
  -H "X-API-Key: <tu-key>" -H "Content-Type: application/json" \
  -d '{"title": "Inception", "year": 2010}'
```

Sin key o con una inválida responde `401`. En Swagger UI (`/docs`) usa el botón **Authorize**.
La key es un secreto de servidor: úsala desde scripts, el pipeline de datos o un backend, nunca
la incluyas en un frontend público. Sirve la API solo por HTTPS en producción.

## Endpoints

> Los métodos `POST`, `PUT` y `DELETE` de todas las secciones requieren `X-API-Key`.

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
