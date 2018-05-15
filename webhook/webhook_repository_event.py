from collection_modules.module import convert_datetime
from collections_edges import Repo
from webhook_graphql_queries.webhook_graphql_queries import webhook_repo_query


class GetRepositoryEvent:

    def __init__(self, db):
        self.db = db

    def __create_repository(self, org_name, repo_name, branch):
        repo = Repo(self.db, org=org_name, query=webhook_repo_query, collection_name="Repo", repo_name=repo_name,
                    branch_name=branch)
        repo.collect_webhook()

    def __delete_repository(self, org_name, repo_name, pushed_date):
        self.db.update(obj={"org": org_name, "repo_name": repo_name}, patch={"deleted_at": pushed_date},
                       kind="Repo")

    def __update_repository(self, org_name, repo_name, pushed_date, status, document_name='open_source'):
        self.db.update_generic(obj={"org": org_name, "repo_name": repo_name}, patch={"$addToSet": {document_name:
                                   {"$each": [{"date": pushed_date, "status": status}]}}}, kind="Repo")

    def get_data(self, raw_json):
        action = raw_json['action']
        org_name = raw_json['organization']['login']
        repo_name = raw_json['repository']['name']
        branch = raw_json['repository']['default_branch']
        pushed_date = convert_datetime(raw_json['repository']['pushed_at'])

        if action == "created":
            self.__create_repository(org_name, repo_name, branch)
        elif action == "deleted":
            self.__delete_repository(org_name, repo_name, pushed_date)
        elif action == "publicized":
            self.__update_repository(org_name, repo_name, pushed_date, True)
        elif action == "privatized":
            self.__update_repository(org_name, repo_name, pushed_date, False)
