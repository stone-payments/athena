from datetime import datetime

from collections_edges import Dev
from webhook_graphql_queries.webhook_graphql_queries import webhook_dev_query


class GetDevEvent:

    def __init__(self, db):
        self.db = db

    def __create_dev(self, dev_name):
        Dev(self.db, org=None, query=webhook_dev_query, collection_name="Dev", dev_name=dev_name).collect_webhook()

    def __delete_dev(self, dev_name):
        self.db.update(obj={"login": dev_name}, patch={"deleted_at": datetime.utcnow()},
                       kind="Dev")

    def __update_repository(self, org_name, repo_name, pushed_date, document_name, status):
        self.db.update_generic(obj={"org": org_name, "repo_name": repo_name}, patch={"$addToSet": {document_name:
                                   {"$each": [{"date": pushed_date, "status": status}]}}}, kind="Repo")

    def get_data(self, raw_json):
        dev_name, action = raw_json['membership']['user']['login'], raw_json['action']
        call = {'member_added': self.__create_dev, 'member_removed': self.__delete_dev}
        call[action](dev_name)
