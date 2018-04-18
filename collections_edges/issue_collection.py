from datetime import datetime

from collection_modules.module import find_key, utc_time, convert_datetime
from collection_modules.validators import string_validate, not_null, bool_validate
from collectors_and_savers.collector import CollectorRestricted
from collectors_and_savers.webhook_collector import WebhookCollector
from custom_configurations.config import number_pagination


class Issue:
    def __init__(self, db, org, query, query_db=None, collection_name="Issue", save_queue_type=None, edge_name="edges",
                 repo_name=None, issue_number=None):
        self.issue_number = issue_number
        self.repo_name = repo_name
        self.db = db
        self.org = org
        self.query = query
        self.query_db = query_db
        self.collection_name = collection_name
        self.save_queue_type = save_queue_type
        self.edge_name = edge_name

    def content(self, **kwargs):
        page = kwargs.get('page')
        print(page)
        node = kwargs.get('node')
        print(node)
        save_content = {
            "collection_name": string_validate(self.collection_name),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('issueId', node)),
            "repository_id": not_null(find_key('repository_id', page)),
            "repo_name": string_validate(find_key('repo_name', page)),
            "state": string_validate(find_key('state', node)),
            "closed_login": string_validate(find_key('closed_login', node)),
            "closed_at": convert_datetime(find_key('closed_at', node)),
            "created_login": string_validate(find_key('created_login', node)),
            "created_at": convert_datetime(find_key('createdAt', node)),
            "author_association": string_validate(find_key('authorAssociation', node)),
            "closed": bool_validate(find_key('closed', node)),
            "label": string_validate(find_key('label', node)),
            "title": string_validate(find_key('title', node)),
            "db_last_updated": datetime.utcnow(),
        }
        return save_content

    @staticmethod
    def edges(node):
        save_edges = [
            {
                "edge_name": "issue_to_repo",
                "to": find_key('_id', node),
                "from": find_key('repository_id', node),
                "db_last_updated": datetime.utcnow(),
            }
        ]
        return save_edges

    def collect(self):
        start = CollectorRestricted(db=self.db, collection_name=self.collection_name, org=self.org,
                                    edges=self.edge_name, query=self.query, updated_utc_time=utc_time,
                                    query_db=self.query_db, number_of_repo=number_pagination, save_content=self.content,
                                    save_edges=self.edges)
        start.start(self.save_queue_type)

    def collect_webhook(self):
        start = WebhookCollector(db=self.db, collection_name=self.collection_name, org=self.org,
                                 repo_name=self.repo_name, issue_number=self.issue_number,
                                 edges=self.edge_name, query=self.query, save_content=self.content,
                                 save_edges=self.edges)
        start.start()
