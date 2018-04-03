from collectors_and_savers.collector import *


class Teams:
    def __init__(self, db, org, query, collection_name, edge_name="edges"):
        self.db = db
        self.org = org
        self.query = query
        self.collection_name = collection_name
        self.edge_name = edge_name

    def content(self, _, node):
        save_content = {
            "collection_name": string_validate(self.collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": find_key('teamId', node),
            'createdAt': convert_datetime(find_key('createdAt', node)),
            "teamName": string_validate(node["node"]["name"], not_none=True),
            "privacy": string_validate(node["node"]["privacy"]),
            "slug": string_validate(node["node"]["slug"], not_none=True),
            "membersCount": int_validate(find_key('membersCount', node)),
            "repoCount": int_validate(find_key('repoCount', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    @staticmethod
    def edges(team, members, repos):
        collect_member_of_team = [
            {
                "edge_name": "dev_to_team",
                'to': find_key('_id', team),
                'from': find_key('memberId', member),
                "db_last_updated": datetime.datetime.utcnow(),
            }
            for member in members
        ]
        collect_repositories_of_team = [
            {
                "edge_name": "repo_to_team",
                'to': find_key('_id', team),
                'from': find_key('repoId', repo_slice),
                "db_last_updated": datetime.datetime.utcnow(),
            }
            for repo_slice in repos
        ]
        return collect_member_of_team, collect_repositories_of_team

    def collect(self):
        start = CollectorTeam(db=self.db, collection_name=self.collection_name, org=self.org, edges=self.edge_name,
                              query=self.query, number_of_repo=number_pagination, updated_utc_time=utc_time,
                              save_content=self.content, save_edges=self.edges)
        start.start()
