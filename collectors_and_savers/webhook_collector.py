from collection_modules.module import find_key
from collection_modules.module import client_graphql
import pprint


class Collector:
    def __init__(self, db: object, collection_name: object, org: str, edges: object, query: object,
                 save_content: callable, save_edges: callable, number_of_repo: int = None, branch_name = None,
                 since=None, until=None):
        self.db = db
        self.org = org
        self.query = query
        self.edges_name = edges
        self.number_of_repo = number_of_repo
        self.collection_name = collection_name
        self.save_content = save_content
        self.save_edges = save_edges
        self.branch_name = branch_name
        self.since = since
        self.until = until

    def _collect(self):
        response = client_graphql.execute(self.query, {
                                                   "number_of_repos": self.number_of_repo,
                                                   "org": self.org,
                                                   "branch": self.branch_name,
                                                   "sinceTime": self.since,
                                                   "untilTime": self.until
                                               })
        pprint.pprint(response)
        # for page in return_pagination:
        #     edges = find_key(self.edges_name, page)
        #     self.process_edges(edges, return_pagination=return_pagination, page=page)

    def process_edges(self, edges, **kwargs): pass

    def start(self):
        print('entrei Collector')
        self._collect()
