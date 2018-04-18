from collection_modules.module import find_key
from collections_edges import Issue
from webhook_graphql_queries.webhook_graphql_queries import webhook_issue_query


class GetIssueEvent:

    def __init__(self, db):
        self.db = db

    def __open_issue(self, org_name, repo_name, issue_number):
        issue = Issue(self.db, org=org_name, query=webhook_issue_query, collection_name="Issue", repo_name=repo_name,
                      issue_number=issue_number)
        issue.collect_webhook()

    def __close_issue(self, org_name, repo_name, pushed_date):
        self.db.update(obj={"org": org_name, "repo_name": repo_name}, patch={"deleted_at": pushed_date},
                       kind="Repo")

    def __update_issue(self, org_name, repo_name, pushed_date, document_name, status):
        self.db.update_generic(obj={"org": org_name, "repo_name": repo_name}, patch={"$addToSet": {document_name:
                                   {"$each": [{"date": pushed_date, "status": status}]}}}, kind="Repo")

    def get_data(self, raw_json):
        repository = find_key('repository', raw_json)
        org_name = find_key('login', repository)
        repo_name = find_key('name', repository)
        issue_number = find_key('number', find_key('issue', raw_json))
        action = find_key('action', raw_json)
        if action == "opened" or action == "closed" or action == "reopened":
            self.__open_issue(org_name, repo_name, issue_number)

