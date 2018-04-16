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

    def __update_repository(self, org_name, team_name, new_slug):
        team_id = self.db.query_find_to_dictionary_distinct("Teams", "_id", {"org": org_name, "slug": team_name})
        print(team_id)
        self.db.update(obj={"_id": team_id[0]}, patch={"slug": new_slug}, kind="Teams")

    @staticmethod
    def __get_permission(raw_json):
        write = find_key('push', raw_json)
        admin = find_key('admin', raw_json)
        if (admin):
            return "ADMIN"
        elif (write):
            return "WRITE"
        else:
            return "READ"

    def __get_repository_data(self, org_name, team_name, repo_name):
        team_id = self.db.query_find_to_dictionary_distinct("Teams", "_id", {"org": org_name, "slug": team_name})
        repository_id = self.db.query_find_to_dictionary_distinct("Repo", "_id",
                                                                  {"org": org_name, "repo_name": repo_name})
        return team_id, repository_id

    def __update_team_repository_edges(self, raw_json, org_name, team_name, repo_name, edge_kind):
        permission = self.__get_permission(raw_json)
        team_id, repository_id = self.__get_repository_data(org_name, team_name, repo_name)
        self.db.connect(from_=repository_id[0], to=team_id[0], kind=edge_kind,
                        data={"db_last_updated": datetime.utcnow(), "permission": permission})

    def __delete_team_repository_edges(self, raw_json, org_name, team_name, repo_name, edge_kind):
        permission = self.__get_permission(raw_json)
        team_id, repository_id = self.__get_repository_data(org_name, team_name, repo_name)
        self.db.connect(from_=repository_id[0], to=team_id[0], kind=edge_kind,
                        data={"db_last_updated": datetime.utcnow(), "permission": permission, "deleted_at":
                              datetime.utcnow()})

    def get_data(self, raw_json):
        repository = find_key('repository', raw_json)
        team_name = find_key('slug', find_key('team', raw_json))
        repo_name = find_key('name', repository)
        org_name = find_key('login', find_key('organization', raw_json))
        if find_key('action', raw_json) == "created":
            self.__create_team(org_name, team_name)
        elif find_key('action', raw_json) == "deleted":
            self.__delete_team(org_name, team_name)
        elif find_key('action', raw_json) == "edited":
            if find_key('permissions', find_key('changes', raw_json)):
                self.__update_team_repository_edges(find_key('permissions', repository), org_name, team_name, repo_name,
                                                    "repo_to_team")
            elif find_key('name', find_key('changes', raw_json)):
                old_slug = find_key('name', find_key('changes', raw_json))
                self.__update_repository(org_name, old_slug, find_key('name', find_key('team', raw_json)))
        elif find_key('action', raw_json) == "added_to_repository":
            self.__update_team_repository_edges(find_key('permissions', repository), org_name, team_name, repo_name,
                                                "repo_to_team")
        elif find_key('action', raw_json) == "removed_from_repository":
            self.__delete_team_repository_edges(find_key('permissions', repository), org_name, team_name, repo_name,
                                                "repo_to_team")
