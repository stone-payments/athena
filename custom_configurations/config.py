import os

token = os.getenv("GRAPHQL_TOKEN")
db_name = os.getenv("DB_NAME")
db_url = os.getenv("MONGODB_URL")
username = os.getenv("MONGODB_USER", False)
password = os.getenv("MONGODB_PASS", False)
mongo_port = os.getenv("MONGO_PORT")
url = os.getenv("GITHUB_GRAPHQL_URL")  # GitHub GraphQL API url
url_rest_api = os.getenv("GITHUB_REST_URL")
number_pagination = 100  # Number of items paginated
number_pagination_repositories = 30  # Number of items paginated by repository query
timeout = 25.001
since_time_days_delta = os.getenv("SINCE_TIME_DAYS_DELTA")  # days ago ex: -5
until_time_days_delta = os.getenv("UNTIL_TIME_DAYS_DELTA")  # delta days from now ex: +1
orgs = ["stone-payments", "mundipagg", "pagarme", "cappta", "equals-conc"]
update = 1  # update every x hours
queue_max_size = 1500000
num_of_threads = 1
rest_minutes = 20  # minutes to rest and start collect again
rate_limit_to_sleep = 10  # minimum remaining api value to wait next reset
hash_indexes = [["Dev", "dev_name"], ["Dev", "login"], ["Teams", "team_name"],
                ["Commit", "org"], ["Issue", "repo_name"], ["Repo", "readme"], ["Commit", "author"],
                ["Repo", "repo_name"], ["Repo", "open_source"], ["Repo", "license_id"], ["Repo", "license_type"],
                ["Issue", "close_at"], ["Issue", "created_at"], ["Commit", "committed_date"], ["Fork", "created_at"]]
hash_indexes_unique = []
skip_list_indexes = [["Issue", "close_at"], ["Issue", "created_at"], ["Commit", "committed_date"], ["Fork", "created_at"]]
full_text_indexes = [["Repo", "repo_name"], ["Teams", "team_name"], ["Issue", "org"],
                     ["Commit", "org"], ["Fork", "org"], ["Dev", "login"]]
abuse_time_sleep = 0.7
max_interval = 1  # max interval time for requests
max_retries = 10  # max request retries
