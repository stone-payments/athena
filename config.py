import datetime

token = "896a853e110a21a6e25cbbcf1ebd2e2ce1139a8e"
db_name = "athena_teste"
# db_url = "http://10.152.20.89:8529"
db_url = "http://localhost:8529"
username = "root"
password = ""
url = 'https://api.github.com/graphql'  # GitHub GraphQL API url
urlCommit = 'https://api.github.com/repos/'  # GitHub Rest API url
number_of_repos = 100
timeout = 100.001
since_time = (datetime.datetime.utcnow() + datetime.timedelta(-1)).strftime('%Y-%m-%dT%H:%M:%SZ')
until_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
orgs = ["stone-payments", "mundipagg", "cappta", "equals-conc", "pagarme"]
datetime.datetime.utcnow().strftime("%Y-%m-%d")
update = 1  # update every x hours
batch_size = 20000  # number of results fetched from ArangoDb
queue_max_size = 1500000
num_of_threads = 5
stats_num_of_threads = 2
queue_timeout = 15
stats_queue_timeout = 10
commit_queue_timeout = 25
