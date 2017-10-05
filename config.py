from pyArango.connection import *

###### conection info ##########################################################
token = "896a853e110a21a6e25cbbcf1ebd2e2ce1139a8e"
url = 'https://api.github.com/graphql'
urlCommit = 'https://api.github.com/repos/'
number_of_repos = 50
timeout = 100.001
sinceTime = "2015-09-01T16:10:49Z"
untilTime = "2015-09-30T16:10:49Z"

conn = Connection(username="root", password="")
try:
    db = conn.createDatabase(name="athena2")
except Exception:
    db = conn["athena2"]
