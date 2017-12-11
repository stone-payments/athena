from pymongo import MongoClient
from pymongo import ASCENDING, TEXT

# Create DataBase ################################################


def create_database_if_not_exists(db_name='database', db_url=None):
    if db_url is None:
        raise NameError("DB URL is not Defined")
    client = MongoClient(db_url)
    return client[db_name]


def create_collection_if_not_exists(db, hash_indexes, hash_indexes_unique,
                                    full_text_indexes):
    for hash_index in hash_indexes:
        db[hash_index[0]].create_index([(hash_index[1], ASCENDING)])
    for hash_index_unique in hash_indexes_unique:
        db[hash_index_unique[0]].create_index([hash_index_unique[1], ASCENDING], unique=True)
    for full_text_index in full_text_indexes:
        db[full_text_index[0]].create_index([(full_text_index[1], TEXT)])
