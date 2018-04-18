from collection_modules.module import find_key, utc_time, convert_datetime
from collection_modules.validators import string_validate, not_null, bool_validate
from collectors_and_savers.collector import CollectorRestricted
from custom_configurations.config import number_pagination
from datetime import datetime


class Fork:
    def __init__(self, db, org, query, query_db, collection_name, save_queue_type, edge_name="edges"):
        self.db = db
        self.org = org
        self.query = query
        self.query_db = query_db
        self.collection_name = collection_name
        self.save_queue_type = save_queue_type
        self.edge_name = edge_name

    def content(self, page, node):
        save_content = {
            "collection_name": string_validate(self.collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('forkId', node)),
            "repository_id": not_null(find_key('repository_id', page)),
            "repo_name": string_validate(find_key('repo_name', page)),
            "created_at": convert_datetime(find_key('createdAt', node)),
            "is_private": bool_validate(find_key('isPrivate', node)),
            "is_locked": bool_validate(find_key('isLocked', node)),
            "dev_id": string_validate(find_key('dev_id', node)),
            "login": string_validate(find_key('login', node)),
            "db_last_updated": datetime.utcnow(),
        }
        return save_content

    @staticmethod
    def edges(node):
        save_edges = [{
            "edge_name": "fork_to_dev",
            "to": find_key('_id', node),
            "from": find_key('dev_id', node),
            "db_last_updated": datetime.utcnow(),
        },
            {
                "edge_name": "fork_to_repo",
                "to": find_key('_id', node),
                "from": find_key('repository_id', node),
                "db_last_updated": datetime.utcnow(),
            }
        ]
        return save_edges

    def collect(self):
        start = CollectorRestricted(db=self.db, collection_name=self.collection_name, org=self.org,
                                    edges=self.edge_name, query=self.query, updated_utc_time=utc_time,
                                    query_db=self.query_db, number_of_repo=number_pagination, save_content=self.content,
                                    save_edges=self.edges)
        start.start(self.save_queue_type)
