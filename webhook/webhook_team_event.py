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

    def __get_member(self, org_name, team_name, member_name):
        team_id = self.db.query_find_to_dictionary_distinct("Teams", "_id", {"org": org_name, "slug": team_name})
        member_id = self.db.query_find_to_dictionary_distinct("Dev", "_id", { "login": member_name})
        return team_id, member_id

    def __create_team_member_edges(self, org_name, team_name, member_name):
        try:
            team_id, member_id = self.__get_member(org_name, team_name, member_name)
            self.db.connect(from_=member_id[0], to=team_id[0], kind="dev_to_team",
                            data={"db_last_updated": datetime.utcnow()})
        except Exception as e:
            print(e)

    def __delete_team_member_edges(self, org_name, team_name, member_name):
        team_id, member_id = self.__get_member(org_name, team_name, member_name)
        self.db.connect(from_=member_id[0], to=team_id[0], kind="dev_to_team",
                        data={"db_last_updated": datetime.utcnow(), "deleted_at": datetime.utcnow()})

    @staticmethod
    def __get_permission(raw_json):
        write, admin = find_key('push', raw_json), find_key('admin', raw_json)
        if admin:
            return "ADMIN"
        elif write:
            return "WRITE"
        return "READ"

    def __get_repository_data(self, org_name, team_name, repo_name):
        team_id = self.db.query_find_to_dictionary_distinct("Teams", "_id", {"org": org_name, "slug": team_name})
        repository_id = self.db.query_find_to_dictionary_distinct("Repo", "_id",
                                                                  {"org": org_name, "repo_name": repo_name})
        if team_id and repository_id:
            return team_id, repository_id
        raise Exception("Repository or team null")

    def __update_team_repository_edges(self, raw_json, org_name, team_name, repo_name, edge_kind):
        permission = self.__get_permission(raw_json)
        try:
            team_id, repository_id = self.__get_repository_data(org_name, team_name, repo_name)
            self.db.connect(from_=repository_id[0], to=team_id[0], kind=edge_kind,
                            data={"db_last_updated": datetime.utcnow(), "permission": permission})
        except Exception as e:
            print(e)

    def __delete_team_repository_edges(self, raw_json, org_name, team_name, repo_name, edge_kind):
        permission = self.__get_permission(raw_json)
        try:
            team_id, repository_id = self.__get_repository_data(org_name, team_name, repo_name)
            self.db.connect(from_=repository_id[0], to=team_id[0], kind=edge_kind,
                            data={"db_last_updated": datetime.utcnow(), "permission": permission, "deleted_at":
                                  datetime.utcnow()})
        except Exception as e:
            print(e)

    def get_member_data(self, raw_json):
        team_name = find_key('slug', find_key('team', raw_json))
        member_name = find_key('login', find_key('member', raw_json))
        org_name = find_key('login', find_key('organization', raw_json))
        if find_key('action', raw_json) == "added":
            self.__create_team_member_edges(org_name, team_name, member_name)
        elif find_key('action', raw_json) == "removed":
            self.__delete_team_member_edges(org_name, team_name, member_name)

    def get_data(self, raw_json):
        repository = find_key('repository', raw_json)
        team_name = find_key('slug', find_key('team', raw_json))
        repo_name = find_key('name', repository)
        org_name = find_key('login', find_key('organization', raw_json))
        action = find_key('action', raw_json)
        if action == "created":
            self.__create_team(org_name, team_name)
        elif action == "deleted":
            self.__delete_team(org_name, team_name)
        elif action == "edited":
            if find_key('permissions', find_key('changes', raw_json)):
                self.__update_team_repository_edges(find_key('permissions', repository), org_name, team_name, repo_name,
                                                    "repo_to_team")
            else:
                self.__create_team(org_name, team_name)
        elif action == "added_to_repository":
            self.__update_team_repository_edges(find_key('permissions', repository), org_name, team_name, repo_name,
                                                "repo_to_team")
        elif action == "removed_from_repository":
            self.__delete_team_repository_edges(find_key('permissions', repository), org_name, team_name, repo_name,
                                                "repo_to_team")
