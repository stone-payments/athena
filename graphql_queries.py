with open("queries/repoQuery.aql", "r") as repo_query:
    repo_query = repo_query.read()

with open("queries/devQuery.aql", "r") as dev_query:
    dev_query = dev_query.read()

with open("queries/teamsQuery.aql", "r") as teams_query:
    teams_query = teams_query.read()

with open("queries/commitArango.aql", "r") as commit_arango:
    commit_arango = commit_arango.read()

# commit_arango = "{'committed_today': True, 'org': self.org}"


with open("queries/commitQuery.aql", "r") as commit_query:
    commit_query = commit_query.read()

with open("queries/readmeArango.aql", "r") as readme_arango:
    readme_arango = readme_arango.read()

with open("queries/readmeQuery.aql", "r") as readme_query:
    readme_query = readme_query.read()

with open("queries/statsQuery.aql", "r") as stats_query:
    stats_query = stats_query.read()

with open("queries/forkArango.aql", "r") as fork_arango:
    fork_arango = fork_arango.read()

with open("queries/forkQuery.aql", "r") as fork_query:
    fork_query = fork_query.read()

with open("queries/issueArango.aql", "r") as issue_arango:
    issue_arango = issue_arango.read()

with open("queries/issueQuery.aql", "r") as issue_query:
    issue_query = issue_query.read()

with open("queries/teamsDevArango.aql", "r") as teams_dev_arango:
    teams_dev_arango = teams_dev_arango.read()

with open("queries/teamsDevQuery.aql", "r") as teams_dev_query:
    teams_dev_query = teams_dev_query.read()

with open("queries/teamsRepoArango.aql", "r") as teams_repo_arango:
    teams_repo_arango = teams_repo_arango.read()

with open("queries/teamsRepoQuery.aql", "r") as teams_repo_query:
    teams_repo_query = teams_repo_query.read()
