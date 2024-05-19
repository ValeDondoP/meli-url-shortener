from app.repository.mongo import MongoDBClient
from app.repository.redis import RedisCache
from app.shortener.services import URLShortenerService

def get_url_shortener_service():
    db_repository = MongoDBClient()
    cache_repository = RedisCache()
    return URLShortenerService(db_repository=db_repository, cache_repository=cache_repository)
