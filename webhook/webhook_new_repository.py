from collection_modules.module import find_key
from collections_edges import Repo
from webhook_graphql_queries.webhook_graphql_queries import webhook_repo_query


class GetNewRepository:

    def __init__(self, db):
        self.db = db

    def __create_repository(self, org_name, repo_name, branch):
        repo = Repo(self.db, org=org_name, query=webhook_repo_query, collection_name="Repo", repo_name=repo_name,
                    branch_name=branch)
        repo.collect_webhook()

    def __delete_repository(self, org_name, repo_name, pushed_date):
        self.db.update(obj={"org": org_name, "repo_name": repo_name}, patch={"deleted_at": pushed_date},
                       kind="Repo")

    def __update_repository(self, org_name, repo_name, pushed_date, document_name, status):
        self.db.update_generic(obj={"org": org_name, "repo_name": repo_name}, patch={"$addToSet": {document_name:
                           {"$each": [{"date": pushed_date, "status": status}]}}}, kind="Repo")

    def get_data(self, raw_json):
        org_name = find_key('login', find_key('organization', raw_json))
        repo_name = find_key('name', find_key('repository', raw_json))
        branch = find_key('default_branch', raw_json)
        pushed_date = find_key('pushed_at', raw_json)
        if find_key('action', raw_json) == "created":
            self.__create_repository(org_name, repo_name, branch)
        elif find_key('action', raw_json) == "deleted":
            self.__delete_repository(org_name, repo_name, pushed_date)
        elif find_key('action', raw_json) == "publicized":
            self.__update_repository(org_name, repo_name, pushed_date, "open_source", True)
        elif find_key('action', raw_json) == "privatized":
            self.__update_repository(org_name, repo_name, pushed_date, "open_source", False)
