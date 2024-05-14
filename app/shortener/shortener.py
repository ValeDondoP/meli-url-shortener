from hashlib import md5
from app.repository.mongo import MongoDBClient
from app.repository.redis import RedisCache

class URLShortenerService:
    def __init__(self, db_repository: MongoDBClient, cache_repository: RedisCache):
        self.db_repository = db_repository
        self.cache_repository = cache_repository

    def hash_string(self, url: str) -> str:
        # Generate the shortened URL using MD5 hash
        url_hash = md5(url.encode()).hexdigest()
        return url_hash

    def get_original_url(self, url_hash: str) -> str:
        if self.cache_repository:
            original_url = self.cache_repository.get_original_url(key=url_hash)
            if original_url:
                return original_url

        original_url = self.db_repository.get_document_by_key(key=url_hash)

        if original_url:
            self.cache_repository.set_short_url(key=url_hash,value=original_url)
            return original_url

        return None

    def short_url(self, original_url: str) -> str:
        url_hash = self.hash_string(url=original_url)[:7]

        if not self.get_original_url(url_hash=url_hash):
            self.db_repository.insert_document(url_hash=url_hash, original_url=original_url)
            self.cache_repository.set_short_url(key=url_hash,value=original_url)

        return url_hash
