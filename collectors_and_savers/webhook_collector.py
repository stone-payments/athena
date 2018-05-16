import pprint

from collection_modules.module import client_graphql_webhook
from collection_modules.module import find_key
from collection_modules.validators import validate_edge


class WebhookCollector:
    def __init__(self, db: callable, collection_name: object, edges: object, query: object, save_content: callable,
                 save_edges: callable, org: str = None, number_of_repo: int = None, branch_name=None,
                 since=None, until=None, repo_name=None, dev_name=None, slug: str =None, issue_number: int = None):
        self.issue_number = issue_number
        self.slug = slug
        self.dev_name = dev_name
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
                                                   "repo": self.repo_name,
                                                   "dev": self.dev_name,
                                                   "branch": self.branch_name,
                                                   "since": self.since,
                                                   "until": self.until,
                                                   "slug": self.slug,
                                                   "issue_number": self.issue_number
                                               }
        print(var)
        return client_graphql_webhook.execute(self.query, {
                                                   "number_of_repos": self.number_of_repo,
                                                   "org": self.org,
                                                   "repo" : self.repo_name,
                                                   "dev": self.dev_name,
                                                   "branch": self.branch_name,
                                                   "since": self.since,
                                                   "until": self.until,
                                                   "slug": self.slug,
                                                   "issue_number": self.issue_number
                                               })

    def __content(self, response):
        edges = find_key("edges", response)
        if edges:
            for page in edges:
                content = self.save_content(page=response, node=page)
                self.__save_edges(content, self.save_edges)
        else:
            print("foi")
            content = self.save_content(node=response, page=response)
            self.__save_edges(content, self.save_edges)

    def __content_team(self, response):
        content = self.save_content(node=response)
        self.__save_edges_teams(response, content, self.save_edges)

    def __save_edges(self, save: dict, save_edges: type):
        self.__save_content(save)
        edges = save_edges(save)
        edges = [edge for edge in edges if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name"))]
        for edge in edges:
            self.db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                            data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                           'edge_name']})

    def __save_content(self, save: dict):
        existed_branch = self.db.query("Commit", {"_id": save["_id"]}, {"_id": 0, "branch_name": 1})
        self.db.update(obj={"_id": save["_id"]}, patch=save, kind=save["collection_name"])
        if existed_branch:
            self.db.update_generic(obj={"_id": save["_id"]}, patch={"$addToSet": {"branch_name":
                                                                                      {"$each": existed_branch[0][
                                                                                          "branch_name"]}}},
                                   kind=save["collection_name"])

    def __save_edges_teams(self, response: dict, save: dict, save_edges: type):
        self.__save_content(save)
        members, repositories = save_edges(content=save, members=find_key("members_edge", response),
                                           repos=find_key("repo_edge", response))
        edges = [edge for edge in members if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name"))]
        for edge in edges:
            self.db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                            data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                           'edge_name']})

    def start(self):
        response = self._collect()
        pprint.pprint(response)
        self.__content(response)

    def start_team(self):
        response = self._collect()
        self.__content_team(response)
