# Desafío Meli acortador de URL
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
Con este endpoint se puede con la url corta redirigir a la original. Este endpoint tiene como parámetros url_hash y url_shortener_service que es un servicio que nos va ayudar a obtener a url original desde la base de datos

