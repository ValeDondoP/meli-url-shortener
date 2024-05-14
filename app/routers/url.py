from fastapi import APIRouter, Request
from pydantic import BaseModel, HttpUrl
from app.repository.mongo import MongoDBClient
from app.repository.redis import RedisCache
from app.shortener.shortener import URLShortenerService
from fastapi.responses import RedirectResponse


router = APIRouter()
mongo_db_client = MongoDBClient()
redis_cache = RedisCache()

# Instanciar el servicio URLShortenerService como una variable global
url_shortener_service = URLShortenerService(db_repository=mongo_db_client, cache_repository=redis_cache)

class URLInput(BaseModel):
    original_url: HttpUrl


@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/shorten")
async def shorten_url(request: Request, url_input: URLInput):

    original_url = url_input.original_url
    # Lógica para acortar la URL y guardarla en MongoDB

    url_hash = url_shortener_service.short_url(original_url=original_url)
    # Devolver la URL acortada
    return {"short_url": f"http://localhost:8000/{url_hash}"}


@router.get("/{url_hash}")
def retrieve_url(url_hash: str):
    original_url = url_shortener_service.get_original_url(url_hash=url_hash)

    response = RedirectResponse(url=original_url, status_code=301)

    # Devuelve la instancia de RedirectResponse
    return response