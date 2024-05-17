import json
import pytest
from unittest import mock
from app.shortener.services import URLShortenerService


class TestURLShortenerService:
    def setup_method(self):
        self.mock_db_repository = mock.Mock()
        self.mock_cache_repository = mock.Mock()

        self.shortener_service = URLShortenerService(
            db_repository=self.mock_db_repository,
            cache_repository=self.mock_cache_repository
        )

    def test_get_data_by_hash_in_cache(self):
        fake_hash = "123"

        json_result = '{"hash":123}'
        expected_result = json.loads(json_result)

        self.mock_cache_repository.get_data_by_hash.return_value = json_result

        result = self.shortener_service.get_data_by_hash(url_hash=fake_hash)

        assert result == expected_result
        self.mock_cache_repository.get_data_by_hash.assert_called_once_with(key=fake_hash)

    def test_get_data_by_hash_in_db(self):
        fake_hash = "123"

        json_result = '{"hash":123}'
        expected_result = json.loads(json_result)

        self.mock_cache_repository.get_data_by_hash.return_value = None
        self.mock_db_repository.get_document_by_key.return_value = expected_result

        result = result = self.shortener_service.get_data_by_hash(url_hash=fake_hash)

        assert result == expected_result
        self.mock_cache_repository.get_data_by_hash.assert_called_once_with(key=fake_hash)
        self.mock_db_repository.get_document_by_key.assert_called_once_with(key=fake_hash)

    def test_get_data_by_hash_data_does_not_exists(self):
        fake_hash = "123"

        self.mock_cache_repository.get_data_by_hash.return_value = None
        self.mock_db_repository.get_document_by_key.return_value = None

        result = self.shortener_service.get_data_by_hash(url_hash=fake_hash)
        assert result == None

    @mock.patch("app.shortener.services.URLShortenerService.get_data_by_hash")
    def test_create_short_url_hash_not_in_db(self, mock_get_data_by_hash):
        original_url = "http://example.com"
        url_hash = "a9b9f04"
        mock_get_data_by_hash.return_value = None
        self.mock_db_repository.get_document_by_key.return_value = {"fake":"document"}

        result = self.shortener_service.create_short_url(original_url=original_url)

        assert result == url_hash
        mock_get_data_by_hash.assert_called_once_with(url_hash=url_hash)
        self.mock_db_repository.get_document_by_key.assert_called_once()
        self.mock_cache_repository.set_short_url.assert_called_once()

    @mock.patch("app.shortener.services.URLShortenerService.get_data_by_hash")
    def test_create_short_url_hash_not_in_db_error(self, mock_get_data_by_hash):
        original_url = "http://example.com"

        mock_get_data_by_hash.return_value = None
        self.mock_db_repository.get_document_by_key.side_effect = RuntimeError

        with pytest.raises(RuntimeError):
            self.shortener_service.create_short_url(original_url=original_url)

    @mock.patch("app.shortener.services.URLShortenerService.get_data_by_hash")
    def test_create_short_url_hash_in_db(self,mock_get_data_by_hash):
        original_url = "http://example.com"
        url_hash = "a9b9f04"

        result = self.shortener_service.create_short_url(original_url=original_url)

        assert result == url_hash
        mock_get_data_by_hash.assert_called_once_with(url_hash=url_hash)

        self.mock_db_repository.insert_document.assert_not_called()
        self.mock_cache_repository.set_short_url.assert_not_called()
        self.mock_db_repository.get_document_by_key.assert_not_called()