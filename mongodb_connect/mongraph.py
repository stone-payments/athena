from pymongo import MongoClient
from pymongo import ASCENDING, TEXT


class Mongraph(object):
    def __init__(self, db_name, db_url, hash_indexes, hash_indexes_unique,
                 full_text_indexes):
        self.hash_indexes_unique = hash_indexes_unique
        self.full_text_indexes = full_text_indexes
        self.hash_indexes = hash_indexes
        self.db_name = db_name
        self.db_url = db_url
        self._mongodb_client = self.create_database_if_not_exists()

    def update(self, obj: object, patch: object, kind: str = None):
        collection_name = kind
        collection = self._mongodb_client[collection_name]
        collection.update_many(obj, {"$set": patch}, upsert=True)

    def connect(self, from_: str, to: str, kind: str, data: dict):
        kind = kind or '{from}${to}'.format(**{
            'from': from_,
            'to': to
        })
        edge_id = str(from_) + str(to)
        self.update(obj={"_id": edge_id}, patch={"from": from_, "to": to, "type": kind, "data": data}, kind="edges")

    def create_database_if_not_exists(self):
        if self.db_url is None:
            raise NameError("DB URL is not Defined")
        client = MongoClient(self.db_url)
        _db = client[self.db_name]
        self.create_collection_if_not_exists(_db)
        return _db

    def create_collection_if_not_exists(self, db):
        for hash_index in self.hash_indexes:
            db[hash_index[0]].create_index([(hash_index[1], ASCENDING)])
        for hash_index_unique in self.hash_indexes_unique:
            db[hash_index_unique[0]].create_index([hash_index_unique[1], ASCENDING], unique=True)
        for full_text_index in self.full_text_indexes:
            db[full_text_index[0]].create_index([(full_text_index[1], TEXT)])

    def query(self, collection, query, projection):
        return [dict(x) for x in self._mongodb_client[collection].find(query, projection)]


def list_reponse_query(db, collection, query, projection, key_to_be_returned):
    response = db.query(collection, query, projection)
    return [str(value[key_to_be_returned]) for value in response]
