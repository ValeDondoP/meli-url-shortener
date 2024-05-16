import json
from hashlib import md5
from app.models.url import URLInputUpdate


class URLShortenerService:
    def __init__(self, db_repository, cache_repository):
        self.db_repository = db_repository
        self.cache_repository = cache_repository

    def generate_url_from_params(self,document: URLInputUpdate) -> str:
        protocol = document.protocol
        domain = document.domain
        path = document.path.lstrip('/') if document.path else None  # Eliminar la barra inicial si está presente
        params = document.params

        url = f"{protocol}://{domain}"

        # Añadir el path si existe
        if path:
            url += f"/{path}"

        if params:
            params_list = []
            for k,v in params.items():
                params_list.append(f"{k}={v}")

            params = "&".join(params_list)
            url+= "?" + params

        return url


    def hash_string(self, url: str) -> str:
        # Generate the shortened URL using MD5 hash
        url_hash = md5(url.encode()).hexdigest()
        return url_hash

    def get_data_by_hash(self, url_hash: str):
        document_json = self.cache_repository.get_data_by_hash(key=url_hash)
        if document_json:
            document = json.loads(document_json)
            return document

        document = self.db_repository.get_document_by_key(key=url_hash)

        if document:
            document_json = json.dumps(document)
            self.cache_repository.set_short_url(key=url_hash,value=document_json)
            return  document

        return None

    def create_short_url(self, original_url: str) -> str:
        url_hash = self.hash_string(url=original_url)[:7]

        if not self.get_data_by_hash(url_hash=url_hash):
            self.db_repository.insert_document(url_hash=url_hash, original_url=original_url)

            document = self.db_repository.get_document_by_key(key=url_hash)
            document_json = json.dumps(document)

            self.cache_repository.set_short_url(key=url_hash,value=document_json)

        return url_hash

    def toggle_enabled(self, url_hash: str, enabled: bool) -> bool:
        document = self.get_data_by_hash(url_hash=url_hash)
        if not document:
            return False

        update_fields = {"enabled": enabled}
        if self.db_repository.update_document(key=url_hash, update_fields=update_fields):
            if not enabled:
                self.cache_repository.delete(key=url_hash)
            else:
                self.cache_repository.update_fields(key=url_hash, fields=update_fields)

            return True

        return False

    def is_url_enabled(self, url_hash: str) -> bool:
       return self.db_repository.is_document_url_enabled(key=url_hash)

    def update_url_hash(self, url_hash: str, url_input: URLInputUpdate) -> bool:
        new_url = self.generate_url_from_params(document=url_input)
        update_fields =  {
            "original_url": new_url,
            "enabled": True,
            "visited": 0
        }

        is_updated = self.db_repository.update_document(key=url_hash, update_fields=update_fields)
        if is_updated:
            # update cache
            if self.cache_repository.get_data_by_hash(key=url_hash):
                self.cache_repository.update_fields(key=url_hash,fields=update_fields)

            return True

        return False

