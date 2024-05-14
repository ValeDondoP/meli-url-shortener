from hashlib import md5
from app.repository.mongo import MongoDBClient
from app.repository.redis import RedisCache
import json

class URLShortenerService:
    def __init__(self, db_repository: MongoDBClient, cache_repository: RedisCache):
        self.db_repository = db_repository
        self.cache_repository = cache_repository

    def hash_string(self, url: str) -> str:
        # Generate the shortened URL using MD5 hash
        url_hash = md5(url.encode()).hexdigest()
        return url_hash

    def get_original_url(self, url_hash: str):
        if self.cache_repository:
            document_json = self.cache_repository.get_original_url(key=url_hash)
            if document_json:
                document = json.loads(document_json)
                return document

        document = self.db_repository.get_document_by_key(key=url_hash)

        if document:
            document_json = json.dumps(document)
            self.cache_repository.set_short_url(key=url_hash,value=document_json)
            return  document

        return None

    def short_url(self, original_url: str) -> str:
        url_hash = self.hash_string(url=original_url)[:7]

        if not self.get_original_url(url_hash=url_hash):
            self.db_repository.insert_document(url_hash=url_hash, original_url=original_url)
            document = self.db_repository.get_document_by_key(key=url_hash)
            document_json = json.dumps(document)
            self.cache_repository.set_short_url(key=url_hash,value=document_json)

        return url_hash

    def toggle_enabled(self, url_hash: str, enabled: bool) -> bool:
        document = self.get_original_url(url_hash=url_hash)
        if not document:
            return False

        if self.db_repository.update_document(key=url_hash, enabled=enabled):
            if not enabled:
                self.cache_repository.delete(key=url_hash)

            return True

        return False

    def is_url_enabled(self, url_hash: str) -> bool:
       return self.db_repository.is_document_url_enabled(key=url_hash)

