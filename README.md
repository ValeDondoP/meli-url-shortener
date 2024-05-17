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
create_shorten_url(
    url_input: URLInput,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ) puedes explicar lo de inyeccionde dependencaias
```

