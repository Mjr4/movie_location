from app.database import SessionLocal, engine
from app.models import Base, Movie, Location, MovieLocation

Base.metadata.create_all(bind=engine)

db = SessionLocal()

movies = [
    Movie(title="The Dark Knight", year=2008, director="Christopher Nolan", genre="Acción", imdb_id="tt0468569"),
    Movie(title="Inception", year=2010, director="Christopher Nolan", genre="Ciencia Ficción", imdb_id="tt1375666"),
    Movie(title="The Godfather", year=1972, director="Francis Ford Coppola", genre="Drama", imdb_id="tt0068646"),
    Movie(title="Interstellar", year=2014, director="Christopher Nolan", genre="Ciencia Ficción", imdb_id="tt0816692"),
    Movie(title="Gladiator", year=2000, director="Ridley Scott", genre="Acción", imdb_id="tt0172495"),
]

locations = [
    Location(name="Chicago Loop", location_type="exterior", city="Chicago", country="Estados Unidos",
              latitude=41.8827, longitude=-87.6233, description="Centro financiero de Chicago"),
    Location(name="Battersea Power Station", location_type="exterior", city="Londres", country="Reino Unido",
              latitude=51.4836, longitude=-0.1449, description="Central eléctrica icónica a orillas del Támesis"),
    Location(name="Pinewood Studios", location_type="interior", city="Buckinghamshire", country="Reino Unido",
              latitude=51.5466, longitude=-0.5413, description="Estudios cinematográficos históricos"),
    Location(name="Staten Island", location_type="exterior", city="Nueva York", country="Estados Unidos",
              latitude=40.5795, longitude=-74.1502, description="Barrio de Nueva York"),
    Location(name="Museo di Palazzo Ducale", location_type="exterior", city="Génova", country="Italia",
              latitude=44.4056, longitude=8.9463, description="Palacio ducal usado para escenas de época"),
    Location(name="Wadi Rum", location_type="exterior", city="Wadi Rum", country="Jordania",
              latitude=29.5760, longitude=35.4157, description="Desierto de arena roja usado como planeta alienígena"),
    Location(name="Fort Ricasoli", location_type="exterior", city="Kalkara", country="Malta",
              latitude=35.8939, longitude=14.5353, description="Fortaleza del siglo XVII usada como Roma antigua"),
]

db.add_all(movies)
db.add_all(locations)
db.commit()

# Refrescar para obtener IDs
for m in movies:
    db.refresh(m)
for l in locations:
    db.refresh(l)

movie_locations = [
    MovieLocation(movie_id=movies[0].id, location_id=locations[0].id,
                  scene_description="Persecución del Joker por las calles de Gotham"),
    MovieLocation(movie_id=movies[0].id, location_id=locations[1].id,
                  scene_description="Exterior del edificio Wayne Enterprises"),
    MovieLocation(movie_id=movies[1].id, location_id=locations[2].id,
                  scene_description="Escenas del sueño en el laberinto"),
    MovieLocation(movie_id=movies[1].id, location_id=locations[0].id,
                  scene_description="Secuencia del tren subterráneo"),
    MovieLocation(movie_id=movies[2].id, location_id=locations[3].id,
                  scene_description="Casa de la familia Corleone"),
    MovieLocation(movie_id=movies[2].id, location_id=locations[4].id,
                  scene_description="Escenas del bautizo en Italia"),
    MovieLocation(movie_id=movies[3].id, location_id=locations[5].id,
                  scene_description="Planeta desconocido con gravedad extrema"),
    MovieLocation(movie_id=movies[4].id, location_id=locations[6].id,
                  scene_description="Coliseo romano y escenas de batalla"),
]

db.add_all(movie_locations)
db.commit()
db.close()

print("✓ Datos de prueba insertados correctamente")
print(f"  {len(movies)} películas")
print(f"  {len(locations)} locaciones")
print(f"  {len(movie_locations)} asociaciones")
