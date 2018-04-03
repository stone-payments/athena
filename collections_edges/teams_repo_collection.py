from collectors_and_savers.collector import *


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
        save_content = {
        }
        return save_content

    @staticmethod
    def edges(response, node):
        save_edges = [{
            "edge_name": "repo_to_team",
            'to': find_key('teamId', response),
            'from': find_key('repoId', node),
            "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    def collect(self):
        start = CollectorRestrictedTeam(db=self.db, org=self.org, edges=self.edges_name, query=self.query,
                                        query_db=self.query_db, number_of_repo=number_pagination,
                                        save_content=self.content, save_edges=self.edges)
        start.start(self.save_queue_type)
