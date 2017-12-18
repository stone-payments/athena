from collectors_and_savers.collector import *


def dev(db, org, query, collection_name, edge_name="edges"):
    def content(**kwargs):
        node = kwargs.get('node')
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "_id": find_key("id", node),
            "devName": string_validate(find_key("name", node)),
            "followers": int_validate(node["node"]["followers"]["totalCount"]),
            "following": int_validate(node["node"]["following"]["totalCount"]),
            "login": string_validate(node["node"]["login"], not_none=True),
            "avatarUrl": string_validate(node["node"]["avatarUrl"]),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(*_):
        save_edges = [
        ]
        return save_edges

    start = CollectorGeneric(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                             number_of_repo=number_of_repos, updated_utc_time=utc_time,
                             save_content=content, save_edges=edges)
    start.start()
