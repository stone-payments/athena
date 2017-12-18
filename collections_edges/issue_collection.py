from collectors_and_savers.collector import *


def issue(db, org, query, query_db, collection_name, save_queue_type, edge_name="edges", ):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('issueId', node)),
            "repositoryId": not_null(find_key('repositoryId', response)),
            "repoName": string_validate(find_key('repoName', response)),
            "state": string_validate(find_key('state', node)),
            "closed_login": string_validate(find_key('closed_login', node)),
            "closedAt": convert_datetime(find_key('closedAt', node)),
            "created_login": string_validate(find_key('created_login', node)),
            "createdAt": convert_datetime(find_key('createdAt', node)),
            "authorAssociation": string_validate(find_key('authorAssociation', node)),
            "closed": bool_validate(find_key('closed', node)),
            "label": string_validate(find_key('label', node)),
            "title": string_validate(find_key('title', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [
            {
                "edge_name": "issue_to_repo",
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
