import datetime

token = ""
db_name = "athena1"
# db_url = "http://10.152.20.89:8529"
db_url = "http://localhost:8529"
username = "root"
password = ""
url = 'https://api.github.com/graphql'
urlCommit = 'https://api.github.com/repos/'
number_of_repos = 50
timeout = 100.001
sinceTime = (datetime.datetime.utcnow() + datetime.timedelta(-1)).strftime('%Y-%m-%dT%H:%M:%SZ')
untilTime = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
orgs = ["stone-payments", "mundipagg", "cappta", "equals-conc", "pagarme"]
datetime.datetime.utcnow().strftime("%Y-%m-%d")
update = 1  # update every x hours
