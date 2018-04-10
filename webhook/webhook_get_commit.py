from collection_modules.module import find_key
import datetime
from collections_edges import Commit, Repo
from webhook_graphql_queries.webhook_graphql_queries import webhook_commits_query, webhook_repo_query


class GetCommit:

    def __init__(self, db):
        self.db = db

    @staticmethod
    def __parse_date(date):
        if date is None:
            return None
        if len(date) == 25:
            timezone = date[-6:-3]
            date = datetime.datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S")
            return (date + datetime.timedelta(hours=-int(timezone))).strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return date

    @staticmethod
    def __parse_branch(data):
        return '/'.join(data.split("/")[2:])

    def __check_repository_updates(self, org, data, repo_name, branch):
        modified_file = find_key("modified", data)
        added_file = find_key("added", data)
        removed_file = find_key("removed", data)
        files = list(set().union(modified_file, added_file, removed_file))
        if "README.md" in files or "readme.md" in files or "CONTRIBUTING.md" in files or "contributing.md" in files or \
                "LICENSE.md" in files or "LICENSE" in files:
            repo = Repo(self.db, org=org, query=webhook_repo_query, collection_name="Repo", repo_name=repo_name,
                        branch_name=branch)
            repo.collect_webhook()

    def get_data(self, raw_json):
        org_name = find_key('login', find_key('organization', raw_json))
        repo_name = find_key('name', find_key('repository', raw_json))
        commit_list = find_key('commits', raw_json)
        branch = self.__parse_branch(find_key('ref', raw_json))
        if not commit_list:
            head_commit = find_key('head_commit', raw_json)
            since_timestamp = until_timestamp = self.__parse_date(find_key('timestamp', head_commit))
        else:
            since_timestamp = self.__parse_date(find_key('timestamp', commit_list[0]))
            until_timestamp = self.__parse_date(find_key('timestamp', commit_list[-1]))
        commit = Commit(self.db, org_name, webhook_commits_query, collection_name="Commit", branch_name=branch,
                        since_commit=since_timestamp, until_commit=until_timestamp, repo_name=repo_name)
        commit.collect_webhook()
        self.__check_repository_updates(org_name, raw_json, repo_name, branch)
