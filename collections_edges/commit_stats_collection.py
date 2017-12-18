from collectors_and_savers.collector import *


def stats_collector(db, org, query, stats_query, collection_name, save_queue_type, edge_name="edges"):
    def content(node, commit_id):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "_id": not_null(commit_id),
            'totalAddDel': int_validate(node['stats']['total']),
            'additions': int_validate(node['stats']['additions']),
            'deletions': int_validate(node['stats']['deletions']),
            'numFiles': int_validate(len(node['files']))
        }
        return save_content

    def edges(_):
        save_edges = [
        ]
        return save_edges

    start = CollectorCommitStats(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                                 query_db=stats_query, number_of_repo=number_of_repos, save_content=content,
                                 save_edges=edges)
    start.start(save_queue_type)
