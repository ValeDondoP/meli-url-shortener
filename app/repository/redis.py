import redis
import json
from typing import Any, Optional

class RedisCache:
    def __init__(self, host: str = 'redis', port: int = 6379, db: int = 0, expire_time: Optional[int] = None):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.expire_time = expire_time

    def get_data_by_hash(self, key: str) -> Optional[Any]:
        value = self.redis_client.get(key)
        if value:
            return value.decode('utf-8')
        return None

    def set_short_url(self, key: str, value: Any) -> None:
        if self.expire_time:
            self.redis_client.setex(key, self.expire_time, value)
        else:
            self.redis_client.set(key, value)

    def delete(self, key: str) -> None:
        self.redis_client.delete(key)

    def update_fields(self, key: str, fields: dict) -> None:
        value = self.redis_client.get(key)

        if value:
            data = json.loads(value)
            for field, new_value in fields.items():
                    data[field] = new_value

            updated_value = json.dumps(data)

            # update redis
            self.redis_client.set(key, updated_value)

    def increment_field(self, key:str, field: str):
        value = self.redis_client.get(key)

        if value:
            data = json.loads(value)

            if field in data:
                data[field] = data[field] + 1

                updated_value = json.dumps(data)
                self.redis_client.set(key, updated_value)