from mongodb_connect.mongraph import list_reponse_query
from collection_modules.module import utc_time_datetime_format


def issue_mongo(self):
    query = {"org": self.org, "issues": {"$gt": 0}, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}
    projection = {'repo_name': 1, '_id': 0}
    collection = 'Repo'
    key_to_be_returned = 'repo_name'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_fork_mongo(self):
    query = {'org': self.org, 'forks': {'$gt': 0}, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}
    projection = {'repo_name': 1, '_id': 0}
    collection = 'Repo'
    key_to_be_returned = 'repo_name'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_team_mongo(self):
    query = {"org": self.org, "membersCount": {"$gt": 100}, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}
    projection = {'slug': 1, '_id': 0}
    collection = 'Teams'
    key_to_be_returned = 'slug'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_commit_mongo(self):
    query = {'committed_today': True, 'org': self.org, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}
    projection = {'repo_name': 1, '_id': 0}
    collection = 'Repo'
    key_to_be_returned = 'repo_name'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def stats_query(self, repository):
    return '{}{}{}{}'.format(self.org, '/', str(repository["repo_name"]), '/commits/')


def query_teams_dev_mongo(self):
    query = {'org': self.org, "membersCount": {'$gt': 100}, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}
    projection = {'slug': 1, '_id': 0}
    collection = 'Teams'
    key_to_be_returned = 'slug'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_teams_repo_mongo(self):
    query = {'org': self.org, "repoCount": {'$gt': 100}, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}
    projection = {'slug': 1, '_id': 0}
    collection = 'Teams'
    key_to_be_returned = 'slug'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)
