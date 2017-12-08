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
    dictionary = [dict(x) for x in self.db.Commit.find({"additions": None, "org": self.org},
                                                       {'repoName': 1, 'oid': 1, '_id': 1})]
    return dictionary


def issue_mongo(self):
    dictionary = [dict(x) for x in self.db.Repo.find({"org": self.org, "issues": {"$gt": 0}},
                                                     {'repoName': 1, '_id': 0})]
    query_list = [str(value["repoName"]) for value in dictionary]
    return query_list


def query_fork_mongo(self):
    dictionary = [dict(x) for x in self.db.Repo.find({"org": self.org, "forks": {"$gt": 0}},
                                                     {'repoName': 1, '_id': 0})]
    query_list = [str(value["repoName"]) for value in dictionary]
    return query_list


def query_team_mongo(self):
    dictionary = [dict(x) for x in self.db.Teams.find({"org": self.org, "membersCount": {"$gt": 100}},
                                                      {'slug': 1, '_id': 0})]
    query_list = [str(value["slug"]) for value in dictionary]
    return query_list


def query_commit_mongo(self):
    dictionary = [dict(x) for x in
                  self.db.Repo.find({'committed_today': True, 'org': self.org}, {'repoName': 1, '_id': 0})]
    query_list = [str(value["repoName"]) for value in dictionary]
    return query_list


def stats_query(self, repository):
    return self.org + "/" + str(repository["repoName"]) + '/commits/'


def query_teams_dev_mongo(self):
    dictionary = [dict(x) for x in self.db.Teams.find({'org': self.org, "membersCount": {'$gt': 100}},
                                                      {'slug': 1, '_id': 0})]
    query_list = [str(value["slug"]) for value in dictionary]
    return query_list


def query_teams_repo_mongo(self):
    dictionary = [dict(x) for x in self.db.Teams.find({'org': self.org, "repoCount": {'$gt': 100}},
                                                      {'slug': 1, '_id': 0})]
    query_list = [str(value["slug"]) for value in dictionary]
    return query_list
