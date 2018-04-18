from collectors_and_savers.collector import CollectorRestricted, find_key, utc_time
from collection_modules.validators import string_validate, not_null, int_validate
from collection_modules.module import convert_datetime
from custom_configurations.config import number_pagination
from collectors_and_savers.webhook_collector import WebhookCollector
import datetime


class Commit:
    def __init__(self, db, org, query, query_db=None, collection_name="Commit", save_queue_type=None, edge_name="edges",
                 branch_name=None, since_commit=None, until_commit=None, repo_name=None):
        self.db = db
        self.org = org
        self.query = query
        self.query_db = query_db
        self.collection_name = collection_name
        self.save_queue_type = save_queue_type
        self.edge_name = edge_name
        self.branch_name = branch_name
        self.until_commit = until_commit
        self.since_commit = since_commit
        self.repo_name = repo_name

    def content(self, **kwargs):
        node = kwargs.get('node')
        response = kwargs.get('page')
        save_content = {
            "collection_name": string_validate(self.collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('commit_id', node)),
            "repository_id": string_validate(find_key('repository_id', response), not_none=True),
            "repo_name": string_validate(find_key('repo_name', response), not_none=True),
            "branch_name": [string_validate(find_key('branch_name', response))],
            "message_head_line": string_validate(find_key('messageHeadline', node)),
            "oid": not_null(find_key('oid', node)),
            "committed_date": convert_datetime(find_key('committedDate', node)),
            "author": string_validate(find_key('login', node)),
            "dev_id": string_validate(find_key('dev_id', node)),
            "commit_id": string_validate(find_key('commit_id', node)),
            'additions': int_validate(find_key('additions', node)),
            'deletions': int_validate(find_key('deletions', node)),
            'num_files': int_validate(find_key('changedFiles', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    @staticmethod
    def edges(node):
        save_edges = [{
            "edge_name": "dev_to_commit",
            "to": find_key('commit_id', node),
            "from": find_key('dev_id', node),
            "db_last_updated": datetime.datetime.utcnow(),
        },
            {
                "edge_name": "repo_to_commit",
                "to": find_key('commit_id', node),
                "from": find_key('repository_id', node),
                "db_last_updated": datetime.datetime.utcnow(),
            },
            {
                "edge_name": "repo_to_dev",
                "to": find_key('dev_id', node),
                "from": find_key('repository_id', node),
                "db_last_updated": datetime.datetime.utcnow(),
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
        start = WebhookCollector(db=self.db, number_of_repo=number_pagination, collection_name=self.collection_name,
                                 org=self.org, branch_name=self.branch_name, until=self.until_commit, since=self.since_commit,
                                 repo_name=self.repo_name, edges=self.edge_name, query=self.query, save_content=self.content,
                                 save_edges=self.edges)
        start.start()
