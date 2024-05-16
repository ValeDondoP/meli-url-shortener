from fastapi import APIRouter, Request, Response, status, HTTPException
from app.repository.mongo import MongoDBClient
from app.repository.redis import RedisCache
from app.shortener.shortener import URLShortenerService
from app.models.url import ToggleURL, URLInput, URLInputUpdate
from fastapi.responses import RedirectResponse


router = APIRouter()
mongo_db_client = MongoDBClient()
redis_cache = RedisCache()


url_shortener_service = URLShortenerService(db_repository=mongo_db_client, cache_repository=redis_cache)


@router.post("/shorten")
async def create_shorten_url(url_input: URLInput, status_code=status.HTTP_201_CREATED):
    original_url = url_input.original_url

    url_hash = url_shortener_service.create_short_url(original_url=original_url)

    return {"short_url": f"http://localhost:8000/{url_hash}"}


@router.get("/shorten/{url_hash}")
async def get_original_url(url_hash: str):
    document_url = url_shortener_service.get_data_by_hash(url_hash=url_hash)
    if document_url:
        return document_url

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")


@router.get("/{url_hash}")
async def retrieve_url(url_hash: str):
    document_url = url_shortener_service.get_data_by_hash(url_hash=url_hash)

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
        return {"Success":"ok"}, status.HTTP_200_OK
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")


@router.put("/update_url_hash/{url_hash}")
async def update_short_url(url_hash:str, url_input: URLInputUpdate):
    try:
        if url_shortener_service.update_url_hash(url_hash=url_hash, url_input=url_input):
            return {"Success":"ok"}, status.HTTP_200_OK

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))