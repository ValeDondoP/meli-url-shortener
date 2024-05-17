import pytest
from unittest import mock
from httpx import AsyncClient
from fastapi import status
from app.main import app
from app.shortener.services import URLShortenerService
from app.dependencies import get_url_shortener_service


# Crear un mock de URLShortenerService
mock_url_shortener_service = mock.Mock(spec=URLShortenerService)


app.dependency_overrides[get_url_shortener_service] = lambda: mock_url_shortener_service


@pytest.mark.asyncio
async def test_create_shorten_url():
    mock_url_shortener_service.create_short_url.return_value = "123"
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        original_url = "http://example.com"
        response = await client.post("/shorten", json={"original_url": original_url})

        assert response.status_code == status.HTTP_200_OK
        assert "short_url" in response.json()


@pytest.mark.asyncio
async def test_get_original_url():
    mock_url_shortener_service.get_data_by_hash.return_value = {"data"}
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/shorten/abc123")

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_original_url_not_found():
    mock_url_shortener_service.get_data_by_hash.return_value = None
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/shorten/abc123")

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_retrieve_url():
    mock_data = {
        "original_url": "http://example.com",
        "enabled": True
        }

    mock_url_shortener_service.get_data_by_hash.return_value = mock_data
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/123")

        assert response.status_code == status.HTTP_301_MOVED_PERMANENTLY
        assert response.headers["location"] == mock_data["original_url"]



@pytest.mark.asyncio
async def test_retrieve_url_invalid_hash():
    mock_url_shortener_service.get_data_by_hash.return_value = None
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/123")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_retrieve_url_not_enabled():
    mock_data = {
        "original_url": "http://example.com",
        "enabled": False
        }

    mock_url_shortener_service.get_data_by_hash.return_value = mock_data
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/123")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_url():
    url_input_data = {
        "protocol":"https",
        "domain":"www.fakedomain.com",
        "path":"products",
        "params":[],
    }

    mock_url_shortener_service.update_url_hash.return_value = True

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.put(f"/update_url_hash/{123}", json=url_input_data)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_url_not_update():
    url_input_data = {
        "protocol":"https",
        "domain":"www.fakedomain.com",
        "path":"products",
        "params":[],
    }
    mock_url_shortener_service.update_url_hash.return_value = None
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.put(f"/update_url_hash/{123}", json=url_input_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


