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
