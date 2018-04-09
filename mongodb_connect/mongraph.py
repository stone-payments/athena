

class Mongraph(object):
    def __init__(self, db):
        self._mongodb_client = db

    def update(self, obj: object, patch: object, kind: str = None):
        collection_name = kind
        collection = self._mongodb_client[collection_name]
        collection.update_many(obj, {"$set": patch}, upsert=True)

    def update_generic(self, obj: object, patch: object, kind: str = None):
        collection_name = kind
        collection = self._mongodb_client[collection_name]
        collection.update_many(obj, patch, upsert=True)

    def connect(self, from_: str, to: str, kind: str, data: dict):
        kind = kind or '{from}${to}'.format(**{
            'from': from_,
            'to': to
        })
        edge_id = str(from_) + str(to)
        self.update(obj={"_id": edge_id}, patch={"from": from_, "to": to, "type": kind, "data": data}, kind="edges")

    def query(self, collection, query, projection):
        return [dict(x) for x in self._mongodb_client[collection].find(query, projection)]

    def query_find_to_dictionary_distinct(self, collection, distinct_key, query):
        return self._mongodb_client[collection].distinct(distinct_key, query)


def list_reponse_query(db, collection, query, projection, key_to_be_returned):
    response = db.query(collection, query, projection)
    return [str(value[key_to_be_returned]) for value in response]
