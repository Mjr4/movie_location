# Movie Location API

API REST construida con FastAPI para gestionar locaciones de filmación de películas. Permite catalogar películas, registrar locaciones geográficas y asociarlas entre sí con descripciones de escenas.

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **SQLite** — base de datos
- **Alembic** — migraciones del esquema
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

## Migraciones

El esquema de la base lo gestiona [Alembic](https://alembic.sqlalchemy.org/); la app ya no crea tablas al
arrancar. Antes del primer uso (y después de cada `git pull` con migraciones nuevas):

```bash
alembic upgrade head
```

**Base creada antes de Alembic** (con datos): haz una copia del `.db` y "adóptala" en vez de recrearla.
`stamp` solo marca la versión inicial sin tocar datos; `upgrade` aplica el resto (renombra una constraint):

```bash
cp movie_locations.db movie_locations.db.bak
alembic stamp a442bfbadc16
alembic upgrade head
```

**Cambiar el esquema**: edita `app/models.py`, genera la migración, revísala y aplícala:

```bash
alembic revision --autogenerate -m "descripción del cambio"
alembic upgrade head
```

`alembic check` avisa si los modelos y las migraciones se desincronizaron (también lo verifica un test).
SQLite no soporta la mayoría de `ALTER TABLE`, por eso `alembic/env.py` usa modo `batch` (recrea la tabla).
Conviene darle nombre explícito a las constraints nuevas: una constraint sin nombre no se puede eliminar por nombre.

## Límite de requests

Cada IP tiene un tope de requests (lecturas y escrituras, incluidos los intentos con key inválida).
Al superarlo responde `429` con el header `Retry-After`. Se configura con `RATE_LIMIT` en el `.env`
(formato de [limits](https://limits.readthedocs.io/): `120/minute`, `10/second`, ...; default `120/minute`).

El contador vive en memoria del proceso: si corres varios workers, cada uno cuenta por separado.
Detrás de un proxy o load balancer, arranca uvicorn con `--proxy-headers --forwarded-allow-ips=<ip-del-proxy>`;
si no, todas las requests parecen venir de la IP del proxy y comparten un solo contador.
Esto frena a un cliente abusivo, no reemplaza la protección contra DDoS de red (CDN, proxy, firewall).

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
├── alembic/
│   └── versions/
├── alembic.ini
├── app/
│   ├── routers/
│   │   ├── movies.py
│   │   ├── locations.py
│   │   ├── movie_locations.py
│   │   └── imports.py
│   ├── main.py
│   ├── auth.py
│   ├── ratelimit.py
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
> clave natural que usa el loader para hacer upsert sin duplicar ni re-geocodificar. Se escribe
> solo desde `POST /import/movies` y solo al insertar.

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
>
> En los listados, `limit` va de 1 a 500 (default 100); fuera de ese rango responde `400`.

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

### Carga masiva — `/import`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/import/movies` | Upsert idempotente de películas con sus locaciones (requiere `X-API-Key`) |

Pensado para el pipeline de datos: un request procesa hasta 200 películas (más de eso responde `400`)
y cuenta como un solo request para el límite de requests.

```json
{"movies": [{
  "imdb_id": "tt0111161", "title": "The Shawshank Redemption", "year": 1994,
  "directors": ["Frank Darabont"], "genres": ["Drama"],
  "locations": [{"name": "Ohio State Reformatory", "city": "Mansfield", "country": "United States",
                 "latitude": 40.7719, "longitude": -82.5115, "source_text": "Mansfield, Ohio, USA"}]
}]}
```

- **Película**: se busca por `imdb_id` (requerido). Si existe, actualiza `title` y `year`; `directors` y
  `genres` **reemplazan** el conjunto (igual que `PUT /movies/{id}`).
- **Locación**: se busca por `latitude`/`longitude` (requeridos, comparación exacta de float, sin redondeo).
  Si existe, actualiza `name`, `city` y `country`; `source_text` solo se escribe al insertar y nunca se pisa.
  Si dos entradas comparten coordenadas gana la última del payload.
- **Asociación**: se crea si no existe y **nunca borra** las que no vengan en el payload ni toca
  `scene_description` / `notes`.
- **Todo o nada**: un request es una transacción. Es idempotente: reenviar el mismo payload no crea filas,
  así que se puede reintentar ante `429`, `503` o timeout. Una carrera concurrente puede dar `409` (reintentable).
- **Errores de validación**: `400` con la ruta del dato inválido, por ejemplo `movies.3.locations.0.latitude`.
- Un `imdb_id` repetido dentro del mismo lote se procesa en orden (la primera crea, la segunda actualiza).

Responde `200` con los conteos del lote. "updated" y "existing" significan que ya existía, haya cambiado o no:

```json
{"movies_created": 1, "movies_updated": 0, "locations_created": 1, "locations_updated": 0,
 "associations_created": 1, "associations_existing": 0}
```
