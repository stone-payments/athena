import os
from pyArango.connection import *
from pymongo import MongoClient

# db_url = "http://10.152.20.89:8529"
db_url = os.getenv("MONGODB_URL")
username = os.getenv("MONGODB_USER")
password = os.getenv("MONGODB_PASS")
# with open("static/assets/js/configs.js", "w") as config_js:
#     config_js.write('let address = "'+os.getenv("API_URL")+'"')

db_name = "athena"
conn = MongoClient(db_url)
db = conn[db_name]

# db.getCollection('edges').aggregate([{$lookup: {from: 'Teams', localField: 'to', foreignField: '_id', as: 'Team'}}
# , {$lookup: {from: 'Dev', localField: 'from', foreignField: '_id', as: 'Dev'}},
# {
#   $match:
# {"Team.0.slug":'plataforma'}
# }
# ])