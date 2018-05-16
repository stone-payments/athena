from datetime import datetime

from collection_modules.module import find_key
from collectors_and_savers.collector import CollectorRestrictedTeam
from custom_configurations.config import number_pagination


class TeamsRepo:
    def __init__(self, db, org, query, query_db, save_queue_type, edges_name="edges"):
        self.db = db
        self.org = org
        self.query = query
        self.query_db = query_db
        self.save_queue_type = save_queue_type
        self.edges_name = edges_name

    @staticmethod
    def content():
        save_content = {}
        return save_content

    @staticmethod
    def edges(response, node):
        save_edges = [{
            "edge_name": "repo_to_team",
            'to': find_key('teamId', response),
            'from': find_key('repoId', node),
            "db_last_updated": datetime.utcnow(),
            "permission": find_key('permission', node)
            }
        ]
        return save_edges

    def collect(self):
        start = CollectorRestrictedTeam(db=self.db, org=self.org, edges=self.edges_name, query=self.query,
                                        query_db=self.query_db, number_of_repo=number_pagination,
                                        save_content=self.content, save_edges=self.edges)
        start.start(self.save_queue_type)
