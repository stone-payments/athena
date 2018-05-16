from app import Collector
from custom_configurations.config import db_name, db_url, username, password, mongo_port, hash_indexes, \
    hash_indexes_unique, full_text_indexes, auth_source
from mongodb_connect.db_connection import DbConnection
from mongodb_connect.mongraph import Mongraph

db_connection = DbConnection(db_name=db_name, db_url=db_url, username=username, password=password,
                             mongo_port=mongo_port, hash_indexes=hash_indexes, hash_indexes_unique=hash_indexes_unique,
                             full_text_indexes=full_text_indexes, auth_source=auth_source).create_db()
db = Mongraph(db=db_connection)

Collector(db=db).start_collector_thread()

