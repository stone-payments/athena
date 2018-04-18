from collection_modules.module import find_key, utc_time
from collection_modules.validators import string_validate
from collectors_and_savers.collector import CollectorGeneric
from collectors_and_savers.webhook_collector import WebhookCollector
from custom_configurations.config import number_pagination
from datetime import datetime


class Dev:
    def __init__(self, db, org, query, collection_name="Dev", edge_name="edges", dev_name=None):
        self.dev_name = dev_name
        self.db = db
        self.org = org
        self.query = query
        self.collection_name = collection_name
        self.edge_name = edge_name

    def content(self, **kwargs):
        node = kwargs.get('node')
        save_content = {
            "collection_name": string_validate(self.collection_name, not_none=True),
            "_id": find_key("id", node),
            "dev_name": string_validate(find_key("name", node)),
            "login": string_validate(find_key("login", node), not_none=True),
            "avatar_url": string_validate(find_key("avatarUrl", node)),
            "db_last_updated": datetime.utcnow(),
        }
        return save_content

    @staticmethod
    def edges(*_):
        save_edges = [
        ]
        return save_edges

    def collect(self):
        start = CollectorGeneric(db=self.db, collection_name=self.collection_name, org=self.org, edges=self.edge_name,
                                 query=self.query, number_of_repo=number_pagination, updated_utc_time=utc_time,
                                 save_content=self.content, save_edges=self.edges)
        start.start()

    def collect_webhook(self):
        start = WebhookCollector(db=self.db, number_of_repo=number_pagination, collection_name=self.collection_name,
                                 org=self.org, until=utc_time(+1), since=utc_time(-1), dev_name=self.dev_name,
                                 edges=self.edge_name, query=self.query,
                                 save_content=self.content, save_edges=self.edges)
        start.start()
