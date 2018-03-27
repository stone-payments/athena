from collection_modules.module import find_key
from collection_modules.module import client_graphql
import pprint
from collection_modules.module import find_key


class Collector:
    def __init__(self, db: callable, collection_name: object, org: str, edges: object, query: object,
                 save_content: callable, save_edges: callable, number_of_repo: int = None, branch_name = None,
                 since=None, until=None, repo_name=None):
        self.repo_name = repo_name
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

        var = {
                                                   "number_of_repos": self.number_of_repo,
                                                   "org": self.org,
                                                   "repo" : self.repo_name,
                                                   "branch": self.branch_name,
                                                   "since": self.since,
                                                   "until": self.until
                                               }
        print(var)
        response = client_graphql.execute(self.query, {
                                                   "number_of_repos": self.number_of_repo,
                                                   "org": self.org,
                                                   "repo" : self.repo_name,
                                                   "branch": self.branch_name,
                                                   "since": self.since,
                                                   "until": self.until
                                               })
        # pprint.pprint(response)
        edges = find_key("edges", response)
        for page in edges:
            content = self.save_content(response, page)
            print(content)
            self.db.update(obj={"_id": content["_id"]}, patch=content, kind=content["collection_name"])
            # self.save_collection(content)

    # def process_edges(self, edges, **kwargs): pass

    def start(self):
        print('entrei Collector')
        self._collect()

    # def process_content(self, ):

    # def save_collection(self, page, node, save: Queue):
    #     queue_input = (self.save_content(page, node), self.save_edges)
    #     save.put(queue_input)
