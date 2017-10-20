import os
from pyArango.connection import *

# db_url = "http://10.152.20.89:8529"
db_url = os.getenv("ARANGODB_URL")
username = os.getenv("ARANGODB_USER")
password = os.getenv("ARANGODB_PASS")
# with open("static/assets/js/configs.js", "w") as config_js:
#     config_js.write('let address = "'+os.getenv("API_URL")+'"')

db_name = "athena"
conn = Connection(arangoURL=db_url, username=username, password=password)
db = conn[db_name]