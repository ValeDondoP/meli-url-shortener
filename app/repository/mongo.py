from pymongo import MongoClient
from typing import Optional, Dict, Any

class MongoDBClient:
    def __init__(self, host: str = 'mongodb', port: int = 27017, db_name: str = 'urldatabase') -> None:
        self.client: MongoClient = MongoClient(host, port)
        self.db = self.client[db_name]

    def insert_document(self, url_hash: str, original_url: str, collection_name: str = "urls") -> None:
        document =  {
            "_id": url_hash,
            "original_url": original_url,
            "enabled": True,
            "visit_count": 0
        }
        collection = self.db[collection_name]
        collection.insert_one(document)

    def get_document_by_key(self, key: str ,collection_name: str = "urls") -> Optional[Dict[str, Any]]:
        collection = self.db[collection_name]
        document = collection.find_one({"_id": key})
        return document

    def update_document(self, key: str, update_fields: dict ,collection_name: str="urls") -> bool:
        collection = self.db[collection_name]
        _filter = {'_id': key}

        result = collection.update_one(_filter, {'$set': update_fields})
        if result.modified_count > 0:
            return True

        return False

    def is_document_url_enabled(self, key: str) -> bool:
        document = self.get_document_by_key(key=key)

        if document and "enabled" in document:
            return document["enabled"]

        return False


    def delete_document(self, collection_name, query):
        pass
