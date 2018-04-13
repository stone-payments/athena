from collectors_and_savers.collector import *
from collectors_and_savers.webhook_collector import WebhookCollector


class Teams:
    def __init__(self, db, org, query, collection_name, edge_name="edges", slug=None):
        self.slug = slug
        self.db = db
        self.org = org
        self.query = query
        self.collection_name = collection_name
        self.edge_name = edge_name

    def content(self, **kwargs):
        node = kwargs.get('node')
        save_content = {
            "collection_name": string_validate(self.collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": find_key('teamId', node),
            'created_at': convert_datetime(find_key('createdAt', node)),
            "team_name": string_validate(find_key('name', node), not_none=True),
            "privacy": string_validate(find_key('privacy', node)),
            "slug": string_validate(find_key('slug', node), not_none=True),
            "members_count": int_validate(find_key('members_count', node)),
            "repo_count": int_validate(find_key('repo_count', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    @staticmethod
    def edges(**kwargs):
        team = kwargs.get('content')
        members = kwargs.get('members')
        repos = kwargs.get('repos')
        # print(members)
        collect_member_of_team = [
            {
                "edge_name": "dev_to_team",
                'to': find_key('_id', team),
                'from': find_key('memberId', member),
                "db_last_updated": datetime.datetime.utcnow(),
                "role": find_key('role', member),

            }
            for member in members
        ]
        collect_repositories_of_team = [
            {
                "edge_name": "repo_to_team",
                'to': find_key('_id', team),
                'from': find_key('repoId', repo_slice),
                "db_last_updated": datetime.datetime.utcnow(),
                "permission": find_key('permission', repo_slice)
            }
            for repo_slice in repos
        ]
        return collect_member_of_team, collect_repositories_of_team

    def collect(self):
        start = CollectorTeam(db=self.db, collection_name=self.collection_name, org=self.org, edges=self.edge_name,
                              query=self.query, number_of_repo=number_pagination_teams, updated_utc_time=utc_time,
                              save_content=self.content, save_edges=self.edges)
        start.start()

    def collect_webhook(self):
        start = WebhookCollector(db=self.db, collection_name=self.collection_name, org=self.org,
                                 slug=self.slug, edges=self.edge_name, query=self.query,
                                 save_content=self.content, save_edges=self.edges)
        start.start_team()
