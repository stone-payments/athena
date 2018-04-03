from collection_modules.module import find_key
import datetime
from collections_edges import Commit, Repo
from app import db
from webhook_graphql_queries.webhook_graphql_queries import webhook_commits_query, webhook_repo_query


class GetCommit:

    @staticmethod
    def __parse_date(date):
        if date is None:
            return None
        timezone = date[-6:-3]
        date = date[:-6]
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        return (date + datetime.timedelta(hours=-int(timezone))).strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def __parse_branch(data):
        return data[11:]

    @staticmethod
    def __check_readme(data, repo_name, branch):
        modified_file = find_key("modified", data)
        print(modified_file)
        if "README.md" in modified_file or "readme.md" in modified_file:
            print("Entrou")
            repo = Repo(db, org="stone-payments", query=webhook_repo_query, collection_name="Repo", repo_name=repo_name,
                        branch_name=branch)
            repo.collect_webhook()

    def get_data(self, raw_json):
        repo_name = find_key('repository', raw_json)
        repo_name = find_key('name', repo_name)
        commit_list = find_key('commits', raw_json)
        if not commit_list:
            head_commit = find_key('head_commit', raw_json)
            since_timestamp = until_timestamp = self.__parse_date(find_key('timestamp', head_commit))
        else:
            since_timestamp = self.__parse_date(find_key('timestamp', commit_list[0]))
            until_timestamp = self.__parse_date(find_key('timestamp', commit_list[-1]))
        branch = self.__parse_branch(find_key('ref', raw_json))
        commit = Commit(db, "stone-payments", webhook_commits_query, collection_name="Commit", branch_name=branch,
                        since_commit=since_timestamp, until_commit=until_timestamp, repo_name=repo_name)
        commit.collect_webhook()
        self.__check_readme(raw_json, repo_name, branch)



