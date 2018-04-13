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

    def __edit_repository_permission(self, raw_json, org_name, team_name, repo_name, pushed_date):
        write = find_key('push', raw_json)
        admin = find_key('admin', raw_json)
        if(admin):
            permission = "ADMIN"
        elif(write):
            permission = "WRITE"
        else:
            permission = "READ"
        team_id = self.db.query_find_to_dictionary_distinct("Teams", "_id", {"org": org_name, "repo_name": repo_name})
        repository_id = self.db.query_find_to_dictionary_distinct("Repo", "_id", {"org": org_name, "team_name": team_name})
        self.db.update(obj={"from": repository_id, "to": team_id, "type": "repo_to_team"},
                       patch={"data.db_last_updated": datetime.utcnow(), "permissions": permission}, kind="edges")

    def get_data(self, raw_json):
        team_name = find_key('slug', find_key('team', raw_json))
        repo_name = find_key('name', find_key('repository', raw_json))
        org_name = find_key('login', find_key('organization', raw_json))
        pushed_date = find_key('pushed_date', find_key('repository', raw_json))
        if find_key('action', raw_json) == "created":
            self.__create_team(org_name, team_name)
        elif find_key('action', raw_json) == "deleted":
            self.__delete_team(org_name, team_name)
        elif find_key('action', raw_json) == "edited":
            if find_key('permissions', find_key('changes', raw_json)):
                self.__edit_repository_permission(find_key('changes', raw_json), org_name, team_name, repo_name, pushed_date)

