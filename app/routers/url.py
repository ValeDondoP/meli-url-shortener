from fastapi import APIRouter, Request, Response, status, HTTPException
from app.repository.mongo import MongoDBClient
from app.repository.redis import RedisCache
from app.shortener.shortener import URLShortenerService
from app.models.url import ToggleURL, URLInput
from fastapi.responses import RedirectResponse


router = APIRouter()
mongo_db_client = MongoDBClient()
redis_cache = RedisCache()


url_shortener_service = URLShortenerService(db_repository=mongo_db_client, cache_repository=redis_cache)


@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/shorten")
async def shorten_url(url_input: URLInput, status_code=status.HTTP_201_CREATED):
    original_url = url_input.original_url

    url_hash = url_shortener_service.short_url(original_url=original_url)

    return {"short_url": f"http://localhost:8000/{url_hash}"}


@router.get("/{url_hash}")
async def retrieve_url(url_hash: str):
    document_url = url_shortener_service.get_original_url(url_hash=url_hash)

    if not document_url:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    else:
        if document_url["enabled"]:
            return RedirectResponse(url=document_url["original_url"], status_code=status.HTTP_301_MOVED_PERMANENTLY)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not active")


@router.put("/{url_hash}")
async def enable_disable_url(url_hash:str, enabled: ToggleURL):
    if url_shortener_service.toggle_enabled(url_hash=url_hash, enabled=enabled.enabled):
        return {"Sucess":"ok"}, status.HTTP_200_OK
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")