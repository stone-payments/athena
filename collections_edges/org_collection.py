from datetime import datetime

from collection_modules.module import find_key, utc_time
from collection_modules.validators import string_validate, not_null, int_validate
from collectors_and_savers.collector import CollectorGeneric
from custom_configurations.config import number_pagination_repositories


class OrgCollection:
    def __init__(self, db, org, query, collection_name, edge_name="edges"):
        self.db = db
        self.org = org
        self.query = query
        self.collection_name = collection_name
        self.edge_name = edge_name

    def content(self, **kwargs):
        page = kwargs.get('page')
        org_name = kwargs.get('org')
        save_content = {
            "collection_name": string_validate(self.collection_name, not_none=True),
            "org": string_validate(org_name, not_none=True),
            "_id": not_null(find_key('id', page)),
            "avatar_url": string_validate(find_key('avatarUrl', page)),
            "description": string_validate(find_key('description', page)),
            "members_count": int_validate(find_key('members_count', page)),
            "teams_Count": int_validate(find_key('teams_Count', page)),
            "repo_count": int_validate(find_key('repo_count', page)),
            "project_count": int_validate(find_key('project_count', page)),
            "db_last_updated": datetime.utcnow(),
        }
        return save_content

    @staticmethod
    def edges(*_):
        save_edges = []
        return save_edges

    def collect(self):
        start = CollectorGeneric(db=self.db, collection_name=self.collection_name, org=self.org, edges=self.edge_name,
                                 query=self.query, number_of_repo=number_pagination_repositories,
                                 updated_utc_time=utc_time, save_content=self.content, save_edges=self.edges)
        start.start()
