# from pymongo import MongoClient


class Mongraph(object):
    def __init__(self, db, edge_collection: str = 'edges'):
        self.__edge_collection = edge_collection
        self.__mongodb_client = db

    def update(self, obj: object, patch: object, kind: str = None):
        collection_name = kind
        collection = self.__mongodb_client[collection_name]
        collection.update_many(obj, {"$set": patch}, upsert=True)

    def connect(self, from_: str, to: str, kind: str, data: dict):
        kind = kind or '{from}${to}'.format(**{
            'from': from_,
            'to': to
        })
        edge_id = str(from_) + str(to)
        self.update(obj={"_id": edge_id}, patch={"from": from_, "to": to, "type": kind, "data": data}, kind="edges")

