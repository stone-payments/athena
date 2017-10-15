from pyArango.connection import *

# Create DataBase ################################################


def create_database_if_not_exists(db_name, db_url, username, password):
    conn = Connection(arangoURL=db_url, username=username, password=password)
    if not conn.hasDatabase(db_name):
        conn.createDatabase(name=db_name)
    return conn[db_name]


def create_collection_if_not_exists(db, collections, hash_indexes, hash_indexes_unique, skip_list_indexes,
                                    full_text_indexes):
    for collection in collections:
        if not db.hasCollection(collection):
            db.createCollection(collection)
    for hash_index in hash_indexes:
        db[hash_index[0]].ensureHashIndex([hash_index[1]], unique=False, sparse=False)
    for hash_index_unique in hash_indexes_unique:
        db[hash_index_unique[0]].ensureHashIndex([hash_index_unique[1]], unique=True, sparse=False)
    for skip_list_index in skip_list_indexes:
        db[skip_list_index[0]].ensureSkiplistIndex([skip_list_index[1]], unique=False, sparse=False)
    for full_text_index in full_text_indexes:
        db[full_text_index[0]].ensureFulltextIndex([full_text_index[1]], minLength=1)

