import datetime
import os

token = os.getenv("GRAPHQL_TOKEN")
# token = "16d5b8dc3cdf1ae8e7c64aa2aec88551b0191dd4"
db_name = "athena"
# db_url = "http://10.152.20.89:8529"
db_url = os.getenv("ARANGODB_URL")
# db_url = "http://localhost:8529"
username = os.getenv("ARANGODB_USER")
# username = "root"
password = os.getenv("ARANGODB_PASS")
# password = ""
# url = 'https://api.github.com/graphql'  # GitHub GraphQL API url
url = os.getenv("GITHUB_GRAPHQL_URL")
# urlCommit = 'https://api.github.com/repos/'  # GitHub Rest API url
urlCommit = os.getenv("GITHUB_REST_URL")
number_of_repos = 100
timeout = 100.001
since_time = (datetime.datetime.utcnow() + datetime.timedelta(-2)).strftime('%Y-%m-%d') + "T00:00:00Z"
until_time = (datetime.datetime.utcnow() + datetime.timedelta(+1)).strftime('%Y-%m-%d') + "T00:00:00Z"
# since_time = "2017-10-10T17:58:18Z"
# until_time = "2017-10-20T17:58:18Z"
orgs = ["stone-payments", "mundipagg", "cappta", "equals-conc", "pagarme"]
datetime.datetime.utcnow().strftime("%Y-%m-%d")
update = 1  # update every x hours
batch_size = 20000  # number of results fetched from ArangoDb
queue_max_size = 1500000
num_of_threads = 5
issue_num_of_threads = 2
stats_num_of_threads = 3
queue_timeout = 15
stats_queue_timeout = 10
commit_queue_timeout = 25
rate_limit_to_sleep = 6  # minimum remaining api value to wait next reset
collections = ["Repo", "Dev", "Teams", "Languages", "LanguagesRepo", "Commit", "DevCommit",
               "RepoCommit", "RepoDev", "Fork", "DevFork", "RepoFork", "Issue", "RepoIssue",
               "TeamsDev", "TeamsRepo"]
hash_indexes = [["Dev", "devName"], ["Dev", "login"], ["Teams", "teamName"],
                ["Commit", "org"], ["Issue", "repoName"], ["Repo", "readme"], ["Commit", "author"],
                ["Repo", "repoName"], ["Repo", "isPrivate"], ["Repo", "licenseId"], ["Repo", "licenseType"]]
hash_indexes_unique = [["Languages", "name"]]
skip_list_indexes = [["Issue", "closeAt"], ["Issue", "createdAt"], ["Commit", "committedDate"], ["Fork", "createdAt"]]
full_text_indexes = [["Repo", "repoName"], ["Repo", "org"], ["Teams", "teamName"], ["Teams", "org"], ["Issue", "org"],
                     ["Commit", "org"], ["Fork", "org"], ["Dev", "login"]]
