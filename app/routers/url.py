import logging
import os
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from app.dependencies import get_url_shortener_service
from app.shortener.services import URLShortenerService
from app.models.url import ToggleURL, URLInput, URLInputUpdate
from fastapi.responses import RedirectResponse


router = APIRouter()

log_directory = "logs"
log_filename = "redirect.log"
log_file_path = os.path.join(log_directory, log_filename)

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(filename=log_file_path, level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/shorten")
async def create_shorten_url(
    url_input: URLInput,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ):
    original_url = url_input.original_url

    url_hash = url_shortener_service.create_short_url(original_url=original_url)

    base_url = os.environ["BASE_URL"]

    return {"short_url": f"{base_url}/{url_hash}"}


@router.get("/shorten/{url_hash}")
async def get_original_url(
    url_hash: str,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ):
    document_url = url_shortener_service.get_data_by_hash(url_hash=url_hash)

    if document_url:
        return document_url

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")


@router.get("/{url_hash}")
async def retrieve_url(
    url_hash: str,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ):
    document_url = url_shortener_service.get_data_by_hash(url_hash=url_hash)
    if not document_url or "original_url" not in document_url:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    else:
        if "enabled" in document_url and document_url["enabled"]:
            logger.info(f"{datetime.now()}-{url_hash}-{document_url['original_url']}")
            url_shortener_service.increment_visit_count(url_hash=url_hash)
            return RedirectResponse(url=document_url["original_url"], status_code=status.HTTP_301_MOVED_PERMANENTLY)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not active")


@router.put("/{url_hash}")
async def enable_disable_url(
    url_hash: str,
    enabled: ToggleURL,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ):
    if url_shortener_service.toggle_enabled(url_hash=url_hash, enabled=enabled.enabled):
        return {"Success":"ok"}, status.HTTP_200_OK
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")


@router.put("/update_url_hash/{url_hash}")
async def update_short_url(
    url_hash:str,
    url_input: URLInputUpdate,
    url_shortener_service: URLShortenerService = Depends(get_url_shortener_service)
    ):
    if url_shortener_service.update_url_hash(url_hash=url_hash, url_input=url_input):
        return {"Success":"ok"}, status.HTTP_200_OK
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
