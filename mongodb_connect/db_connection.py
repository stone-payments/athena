import urllib.parse

from pymongo import ASCENDING, TEXT
from pymongo import MongoClient


class DbConnection:

    def __init__(self, mongo_port, password, username, hash_indexes_unique, full_text_indexes, hash_indexes, db_name,
                 db_url, auth_source):
        self.auth_source = auth_source
        self.mongo_port = mongo_port
        self.password = password
        self.username = username
        self.hash_indexes_unique = hash_indexes_unique
        self.full_text_indexes = full_text_indexes
        self.hash_indexes = hash_indexes
        self.db_name = db_name
        self.db_url = db_url

    def __create_database_if_not_exists(self):
        if self.db_url is None:
            raise NameError("DB URL is not Defined")
        if self.username and self.password:
            password = urllib.parse.quote_plus(self.password)
            username = urllib.parse.quote_plus(self.username)
            client = MongoClient('mongodb://%s:%s@%s:%s/%s?authSource=%s' % (username, password, self.db_url,
                                                                             self.mongo_port, self.db_name,
                                                                             self.auth_source))
        else:
            client = MongoClient('mongodb://%s:%s/%s' % (self.db_url, self.mongo_port, self.db_name))
        _db = client[self.db_name]
        self.__create_collection_if_not_exists(_db)
        return _db

    def __create_collection_if_not_exists(self, db):
        for hash_index in self.hash_indexes:
            db[hash_index[0]].create_index([(hash_index[1], ASCENDING)])
        for hash_index_unique in self.hash_indexes_unique:
            db[hash_index_unique[0]].create_index([hash_index_unique[1], ASCENDING], unique=True)
        for full_text_index in self.full_text_indexes:
            db[full_text_index[0]].create_index([(full_text_index[1], TEXT)])

    def create_db(self):
        return self.__create_database_if_not_exists()
