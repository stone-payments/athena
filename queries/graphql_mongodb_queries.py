from mongodb_connect.mongraph import list_reponse_query

with open("queries/repoQuery.graphql", "r") as repo_query:
    repo_query = repo_query.read()

with open("queries/devQuery.graphql", "r") as dev_query:
    dev_query = dev_query.read()

with open("queries/teamsQuery.graphql", "r") as teams_query:
    teams_query = teams_query.read()

with open("queries/commitQuery.graphql", "r") as commit_query:
    commit_query = commit_query.read()

with open("queries/readmeQuery.graphql", "r") as readme_query:
    readme_query = readme_query.read()

with open("queries/forkQuery.graphql", "r") as fork_query:
    fork_query = fork_query.read()

with open("queries/issueQuery.graphql", "r") as issue_query:
    issue_query = issue_query.read()

with open("queries/teamsDevQuery.graphql", "r") as teams_dev_query:
    teams_dev_query = teams_dev_query.read()

with open("queries/teamsRepoQuery.graphql", "r") as teams_repo_query:
    teams_repo_query = teams_repo_query.read()

with open("queries/org_query.graphql", "r") as org_query:
    org_query = org_query.read()


def query_stats_mongo(self):
    query = {"additions": None, "org": self.org}
    projection = {'repoName': 1, 'oid': 1, '_id': 1}
    collection = 'Commit'
    return self.db.query(collection, query, projection)


def issue_mongo(self):
    query = {"org": self.org, "issues": {"$gt": 0}}
    projection = {'repoName': 1, '_id': 0}
    collection = 'Repo'
    key_to_be_returned = 'repoName'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_fork_mongo(self):
    query = {'org': self.org, 'forks': {'$gt': 0}}
    projection = {'repoName': 1, '_id': 0}
    collection = 'Repo'
    key_to_be_returned = 'repoName'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_team_mongo(self):
    query = {"org": self.org, "membersCount": {"$gt": 100}}
    projection = {'slug': 1, '_id': 0}
    collection = 'Teams'
    key_to_be_returned = 'slug'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_commit_mongo(self):
    query = {'committed_today': True, 'org': self.org}
    projection = {'repoName': 1, '_id': 0}
    collection = 'Repo'
    key_to_be_returned = 'repoName'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def stats_query(self, repository):
    return '{}{}{}{}'.format(self.org, '/', str(repository["repoName"]), '/commits/')


def query_teams_dev_mongo(self):
    query = {'org': self.org, "membersCount": {'$gt': 100}}
    projection = {'slug': 1, '_id': 0}
    collection = 'Teams'
    key_to_be_returned = 'slug'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)


def query_teams_repo_mongo(self):
    query = {'org': self.org, "repoCount": {'$gt': 100}}
    projection = {'slug': 1, '_id': 0}
    collection = 'Teams'
    key_to_be_returned = 'slug'
    return list_reponse_query(self.db, collection, query, projection, key_to_be_returned)
