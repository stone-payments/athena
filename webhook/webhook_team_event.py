from datetime import datetime

from collection_modules.module import find_key
from collections_edges import Teams
from webhook_graphql_queries.webhook_graphql_queries import webhook_team_query


class GetTeamEvent:

    def __init__(self, db):
        self.db = db

    def __create_team(self, org_name, team_name):
        Teams(self.db, org=org_name, query=webhook_team_query, collection_name="Teams", slug=team_name).collect_webhook()

    def __delete_team(self, org_name, team_name):
        self.db.update(obj={"org": org_name, "slug": team_name}, patch={"deleted_at": datetime.utcnow()}, kind="Teams")

    def __update_repository(self, org_name, team_name, pushed_date, document_name, status):
        self.db.update_generic(obj={"org": org_name, "slug": team_name}, patch={"$addToSet": {document_name:
                                   {"$each": [{"date": pushed_date, "status": status}]}}}, kind="Teams")

    def get_data(self, raw_json):
        team_name = find_key('slug', find_key('team', raw_json))
        org_name = find_key('login', find_key('organization', raw_json))
        if find_key('action', raw_json) == "created":
            self.__create_team(org_name, team_name)
        elif find_key('action', raw_json) == "deleted":
            self.__delete_team(org_name, team_name)
