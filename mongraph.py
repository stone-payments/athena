from pymongo import MongoClient


class Mongraph(object):
    def __init__(self, db, edge_collection: str = 'edges'):
        # self.__database = database
        # self.__mongodb_client = mongodb_client
        self.__edge_collection = edge_collection
        self.__mongodb_client = db

    def get(self, obj: object, kind: type = None):
        collection_name = kind.__name__ or type(obj).__name__
        collection = self.__mongodb_client[collection_name]
        with collection.find(obj) as cursor:
            obj = cursor.next()
            return kind(**obj)

    def add(self, obj: object, kind: type = None):
        collection_name = kind.__name__ or type(obj).__name__
        collection = self.__mongodb_client[collection_name]
        collection.insert(obj)

    def remove(self, obj: object, kind: str = None):
        collection_name = kind.__name__ or type(obj).__name__
        collection = self.__mongodb_client[collection_name]
        result = collection.delete_many(obj)
        return result.deleted_count

    def replace(self, obj: object, new: object, kind: str = None):
        collection_name = kind.__name__ or type(obj).__name__
        collection = self.__mongodb_client[collection_name]
        result = collection.replace_one(obj, new)
        return result.modified_count == 1

    def update(self, obj: object, patch: object, kind: str = None):
        collection_name = kind
        collection = self.__mongodb_client[collection_name]
        collection.update_many(obj, {"$set": patch}, upsert=True)
        # return result.modified_count

    def connect(self, from_: str, to: str, kind: str, data: dict):
        kind = kind or '{from}${to}'.format(**{
            'from': from_,
            'to': to
        })
        edge_id = str(from_) + str(to)

        print(kind)
        self.update(obj={"_id": edge_id}, patch={"from": from_, "to": to, "type": kind, "data": data}, kind="edges")

    def disconnect(self, from_: object, to: object, kind: str):
        kind = kind or '{from}${to}'.format(**{
            'from': type(from_).__name__,
            'to': type(to).__name__
        })

    def reconnect(self, from_: object, to: object, kind: str, **fields):
        kind = kind or '{from}${to}'.format(**{
            'from': type(from_).__name__,
            'to': type(to).__name__
        })
