# Desafío acortador de URL
Para este proyecto ocupamos Docker Compose pues simplifica enormemente la configuración, gestión y escalabilidad de aplicaciones.

##### Cómo correr Docker de forma local

* `docker-compose up -d`

##### Reconstruir Docker image

* `docker-compose up --build `

##### Correr los test usando pytest

* `docker exec -it <id_contenedor>  bash`

##### Hostnames para acceder a la app
* Local: http://127.0.0.1:8000

### Arquitectura de Acortador de URL:
Para construir nuestra arquitectura de acortador de URL primero definimos los  principales endpoints de nuestra API. Para nuestra API usé FASTAPI pues es un framework que permite manejar solicitudes de manera extremadamente rápida y eficiente.

##### POST
```python
@router.post("/shorten")
create_shorten_url(
    url_input: URLInput,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ) 
```
Este endpoint se encarga de crear en base de datos y retornar la url corta.
Los parámetros son url_input que es de donde obtendremos nuestra url original y que es del tipo URLInput. URLInput es un BaseModel, que es una clase proporcionada por Pydantic, una biblioteca de validación de datos, que se utiliza para definir y validar datos de entrada y salida de manera estructurada. Por otro lado, tenemos  
el decorador Depends indica a FastAPI que debe llamar a la función get_url_shortener_service para obtener la instancia de URLShortenerService que es un servicio que interactua con la base de datos.


##### GET
```python
    @router.get("/{url_hash}")
    async def retrieve_url(
    url_hash: str,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ):
```
Con este endpoint se puede con la url corta redirigir a la original. Este endpoint tiene como parámetros url_hash y url_shortener_service que es un servicio que nos va ayudar a obtener a url original desde la base de datos.

##### PUT
```python
    @router.put("/update_url_hash/{url_hash}")
    async def update_short_url(
    url_hash:str,
    url_input: URLInputUpdate,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ):
```

Con este endpoint se puede hacer un update de la url de destino. Este endpoint tiene como parámetros url_hash, url_shortener_service y URLInputUpdate que es un base model cuyo schema pide las componentes de una url como el procotolo, dominio,etc por lo que este endpoint puede cambiar cualquier componente de la url de destino.
#### Diseño de la base de datos
Para esta implementación no implementé una tabla usuarios por la simplicidad del sistema, pero se puede haber definido para el caso en que queramos que el sistema sea privado o que al hacer la request podamos guardar información del usuario.

Schemas de mis tablas:
   <img width="659" alt="Captura de Pantalla 2024-05-17 a la(s) 18 04 45" src="https://github.com/ValeDondoP/meli-url-shortener/assets/80803286/d2cc6037-238b-4aab-8c88-244f472c2a52">


En este diseño consideré que las URL se pueden desactivar y también que se pueda saber el número de veces que se ha hecho click en la URL.

Para la elección de la base de datos elegí MongoDb. Esto ya que no existen relaciones  entre las tablas exceptuando por user_id y además como nuestro sistema es read-heavy se esperan millones de request a nuestro sistema y una db no relacional es más fácil de escalar. En adición, en mongodb se puede guardar la información como clave-valor lo que hacer más rápido de acceder.

#### Diseño del sistema
Presento el siguiente diagrama como solución al proyecto
<img width="713" alt="Captura de Pantalla 2024-05-17 a la(s) 19 36 43" src="https://github.com/ValeDondoP/meli-url-shortener/assets/80803286/25042378-9af1-4894-ae56-9488016fb954">


La idea es para dado el número de request usar un balanceador de carga que distribuya de forma equitativa la request a las replicas del server. Para crear una short url se consulta primero si el hash generado ya existe en el Cache, si esta retorna el hash, si no busca si esta en la base de datos.

Por otro lado para el sistema de monitoreo:
Primero, configuraría el registro de eventos importantes en la aplicación. Esto incluiría:

Creación de URLs cortas: Registrar cada vez que un usuario crea una nueva URL corta, incluyendo detalles como la URL original, el hash generado, y la dirección IP del cliente.
Clics en URLs cortas: Registrar cada vez que un usuario hace clic en una URL corta, incluyendo el hash de la URL, la URL original, y la dirección IP del cliente.

Esto lo haría usando logging de python y utilizar log.info y esto se almacena en un file system hdfs y  que las herramientas de monitoreo de logs como Datadog o New Relic para recolectar, almacenar y analizar estos logs desde ahí.

Finalmente haría dashboards en Datadog o New Relic para visualizar las métricas y logs recolectados y podría medir:
Número de URLs creadas: Mostrar la cantidad de nuevas URLs cortas creadas en un período de tiempo.
Clics en URLs: Monitorear la cantidad de clics recibidos por las URLs cortas.
Errores y excepciones: Monitorear cualquier error o excepción que ocurra en la aplicación.
Métricas de rendimiento: Analizar el rendimiento de la aplicación, como el tiempo de respuesta de las solicitudes.


#### Implementación de url shortener
Para mi sistema usé un patrón de capas y patrón repository en donde definí una carpeta repository donde iba a tener definidas dos clases para el acceso a los datos. En este caso como mencioné anteriormente usé Mongodb como base de datos y también usé Redis para usarlo como caché (acceso de datos en memoria).
Aqui va un estracto de las clases que implementan MongoDb y Redis:
```python
class MongoDBClient:
    def __init__(self, host: str = 'mongodb', port: int = 27017, db_name: str = 'urldatabase') -> None:
        self.client: MongoClient = MongoClient(host, port)
        self.db = self.client[db_name]

    def insert_document(self, url_hash: str, original_url: str, collection_name: str = "urls") -> None:
        document =  {
            "_id": url_hash,
            "original_url": original_url,
            "enabled": True,
            "visit_count": 0
        }
        collection = self.db[collection_name]
        collection.insert_one(document)
```
```python
class RedisCache:
    def __init__(self, host: str = 'redis', port: int = 6379, db: int = 0, expire_time: Optional[int] = None):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.expire_time = expire_time

    def get_data_by_hash(self, key: str) -> Optional[Any]:
        value = self.redis_client.get(key)
        if value:
            return value.decode('utf-8')
        return None
```

Por otro lado tenemos el archivo services.py que es donde va a estar nuestra clase URLShortenService que se va a encargar de todos los requerimientos relacionados a la url como acortar la url, obtener la url original para entregarsélo al controlador,etc

``` python
class URLShortenerService:
    def __init__(self, db_repository, cache_repository):
        self.db_repository = db_repository
        self.cache_repository = cache_repository
```
Acá se tiene el método de la clase hash_string, que es el encargado de hacer el hash. En esta implementación vamos a usar el algorimto de hash MD5 que convierte datos en un identificador unico de 128 bits. En el código, url.encode() convierte la URL a bytes, y hashlib.md5(url.encode()) crea un objeto de hash MD5 a partir de esos bytes. Luego, md5_hash.hexdigest() convierte el hash en una cadena hexadecimal de 32 caracteres. Esto genera un identificador único para la url
```python
 def hash_string(self, url: str) -> str:
        # Generate the shortened URL using MD5 hash
        url_hash = md5(url.encode()).hexdigest()
        return url_hash
```
Luego tenemos el siguiente método:
```python
def create_short_url(self, original_url: str) -> str:
        url_hash = self.hash_string(url=original_url)[:7]
        ...
```
Este método llama a la función que genera el hash y toma los primero 7 caracteres
Luego como se explica anteriormente, se pregunta si esta en el caché y si no esta busca en la base de datos.

Finalmente tenemos los siguientes método:
```python
def update_url_hash(self, url_hash: str, url_input: URLInputUpdate) -> bool:
```
Este método se encarga de actualizar las componentes de la url. Primero genera la url a partir de las componentes y luego actualiza la información en la base de datos para el hash asociado.

```python
increment_visit_count(self, url_hash: str) -> bool
```
Este método se encarga de incrementar y guardar en base de datos cuando se hace click a una url corta.

