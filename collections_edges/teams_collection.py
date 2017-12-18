from collectors_and_savers.collector import *


def teams(db, org, query, collection_name, edge_name="edges"):
    def content(self, _, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
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

    start = CollectorTeam(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                          number_of_repo=number_of_repos, updated_utc_time=utc_time,
                          save_content=content, save_edges=edges)
    start.start()
