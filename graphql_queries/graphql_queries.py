def read_query(query):
    with open(query, 'r') as query_response:
        return query_response.read()


repo_query = read_query("graphql_queries/repoQuery.graphql")
dev_query = read_query("graphql_queries/devQuery.graphql")
teams_query = read_query("graphql_queries/teamsQuery.graphql")
commit_query = read_query("graphql_queries/commitQuery.graphql")
readme_query = read_query("graphql_queries/readmeQuery.graphql")
fork_query = read_query("graphql_queries/forkQuery.graphql")
issue_query = read_query("graphql_queries/issueQuery.graphql")
teams_dev_query = read_query("graphql_queries/teamsDevQuery.graphql")
teams_repo_query = read_query("graphql_queries/teamsRepoQuery.graphql")
org_query = read_query("graphql_queries/org_query.graphql")
