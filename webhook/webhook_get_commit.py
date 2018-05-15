import datetime

from collection_modules.module import find_key
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
        files = set().union(modified_file, added_file, removed_file)
        updated = {'README.md', 'readme.md', 'CONTRIBUTING.md', 'contributing.md', 'LICENSE.md', 'LICENSE'}
        if updated.issubset(files):
            repo = Repo(self.db, org=org, query=webhook_repo_query, collection_name="Repo", repo_name=repo_name,
                        branch_name=branch)
            repo.collect_webhook()

    def get_data(self, raw_json):
        org_name, repo_name = raw_json['organization']['login'], raw_json['repository']['name']
        commit_list, branch = raw_json['commits'], self.__parse_branch(raw_json['ref'])
        if not commit_list:
            since_timestamp = until_timestamp = self.__parse_date(raw_json['head_commit']['timestamp'])
        else:
            since_timestamp = self.__parse_date(find_key('timestamp', commit_list[0]))
            until_timestamp = self.__parse_date(find_key('timestamp', commit_list[-1]))
        commit = Commit(self.db, org_name, webhook_commits_query, collection_name="Commit", branch_name=branch,
                        since_commit=since_timestamp, until_commit=until_timestamp, repo_name=repo_name)
        commit.collect_webhook()
        self.__check_repository_updates(org_name, raw_json, repo_name, branch)
