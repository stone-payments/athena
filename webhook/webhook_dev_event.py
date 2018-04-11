from datetime import datetime

from collection_modules.module import find_key
from collections_edges import Dev
from webhook_graphql_queries.webhook_graphql_queries import webhook_dev_query


class GetDevEvent:

    def __init__(self, db):
        self.db = db

    def __create_dev(self, dev_name):
        print(dev_name)
        Dev(self.db, org=None, query=webhook_dev_query, collection_name="Dev", dev_name=dev_name).collect_webhook()

    def __delete_dev(self, dev_name):
        self.db.update(obj={"login": dev_name}, patch={"deleted_at": datetime.utcnow()},
                       kind="Dev")

    def __update_repository(self, org_name, repo_name, pushed_date, document_name, status):
        self.db.update_generic(obj={"org": org_name, "repo_name": repo_name}, patch={"$addToSet": {document_name:
                                   {"$each": [{"date": pushed_date, "status": status}]}}}, kind="Repo")

    def get_data(self, raw_json):
        dev_name = find_key('login', find_key('membership', raw_json))
        print(dev_name)
        if find_key('action', raw_json) == "member_added":
            self.__create_dev(dev_name)
        elif find_key('action', raw_json) == "member_removed":
            self.__delete_dev(dev_name)

