from collectors_and_savers.collector import *


class Dev:
    def __init__(self, db, org, query, collection_name, edge_name="edges"):
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
            "devName": string_validate(find_key("name", node)),
            "followers": int_validate(find_key("totalFollowers", node)),
            "following": int_validate(find_key("totalFollowing", node)),
            "login": string_validate(find_key("login", node), not_none=True),
            "avatarUrl": string_validate(find_key("avatarUrl", node)),
            "db_last_updated": datetime.datetime.utcnow(),
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

# def dev(db, org, query, collection_name, edge_name="edges"):
#     def content(**kwargs):
#         node = kwargs.get('node')
#         save_content = {
#             "collection_name": string_validate(collection_name, not_none=True),
#             "_id": find_key("id", node),
#             "devName": string_validate(find_key("name", node)),
#             "followers": int_validate(find_key("totalFollowers", node)),
#             "following": int_validate(find_key("totalFollowing", node)),
#             "login": string_validate(find_key("login", node), not_none=True),
#             "avatarUrl": string_validate(find_key("avatarUrl", node)),
#             "db_last_updated": datetime.datetime.utcnow(),
#         }
#         return save_content
#
#     def edges(*_):
#         save_edges = [
#         ]
#         return save_edges
#
#     start = CollectorGeneric(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
#                              number_of_repo=number_pagination, updated_utc_time=utc_time,
#                              save_content=content, save_edges=edges)
#     start.start()
