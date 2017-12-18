from collectors_and_savers.collector import *


def fork_collector(db, org, query, query_db, collection_name, save_queue_type, edge_name="edges"):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('forkId', node)),
            "repositoryId": not_null(find_key('repositoryId', response)),
            "repoName": string_validate(find_key('repoName', response)),
            "createdAt": convert_datetime(find_key('createdAt', node)),
            "isPrivate": bool_validate(find_key('isPrivate', node)),
            "isLocked": bool_validate(find_key('isLocked', node)),
            "devId": string_validate(find_key('devId', node)),
            "login": string_validate(find_key('login', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "fork_to_dev",
            "to": find_key('_id', node),
            "from": find_key('devId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        },
            {
                "edge_name": "fork_to_repo",
                "to": find_key('_id', node),
                "from": find_key('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    start = CollectorRestricted(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                                updated_utc_time=utc_time, query_db=query_db,
                                number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(save_queue_type)
