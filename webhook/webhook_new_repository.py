from collection_modules.module import find_key
from collections_edges import Repo
from webhook_graphql_queries.webhook_graphql_queries import webhook_repo_query


class GetNewRepository:

    def __init__(self, db):
        self.db = db

    @staticmethod
    def __parse_branch_string(data):
        return '/'.join(data.split("/")[2:])

    def __create_repository(self, org_name, repo_name, branch):
        repo = Repo(self.db, org=org_name, query=webhook_repo_query, collection_name="Repo", repo_name=repo_name,
                    branch_name=branch)
        repo.collect_webhook()

    def get_data(self, raw_json):
        org_name = find_key('login', find_key('owner', raw_json))
        repo_name = find_key('name', find_key('repository', raw_json))
        branch = self.__parse_branch_string(find_key('master_branch', raw_json))
        self.__create_repository(org_name, repo_name, branch)
