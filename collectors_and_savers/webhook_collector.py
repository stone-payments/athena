from collection_modules.module import client_graphql
from collection_modules.module import find_key
from collection_modules.validators import *
import pprint


class WebhookCollector:
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
        pprint.pprint(response)
        edges = find_key("edges", response)
        if edges:
            for page in edges:
                content = self.save_content(response=response, node=page)
                self.save(content, self.save_edges)
        else:
            print("ELSE")
            content = self.save_content(node=response)
            self.save(content, self.save_edges)

    def save(self, save: dict, save_edges: type):
        existed_branch = self.db.query("Commit", {"_id": save["_id"]}, {"_id": 0, "branch_name": 1})
        self.db.update(obj={"_id": save["_id"]}, patch=save, kind=save["collection_name"])
        if existed_branch:
            self.db.update_generic(obj={"_id": save["_id"]}, patch={"$addToSet": {"branch_name":
                                   {"$each": existed_branch[0]["branch_name"]}}}, kind=save["collection_name"])
        edges = save_edges(save)
        edges = [edge for edge in edges if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name"))]
        for edge in edges:
            self.db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                            data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                           'edge_name']})

    def start(self):
        self._collect()
