def read_query(query):
    with open(query, 'r') as query_response:
        return query_response.read()


webhook_commits_query = read_query("webhook_graphql_queries/webhook_commits.graphql")
webhook_repo_query = read_query("webhook_graphql_queries/webhook_repo.graphql")
