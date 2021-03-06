from collectors_and_savers.collector import *


def teams_repo(db, org, query, query_db, save_queue_type, edges_name="edges"):
    def content(*_):
        save_content = {
        }
        return save_content

    def edges(response, node):
        save_edges = [{
            "edge_name": "repo_to_team",
            'to': find_key('teamId', response),
            'from': find_key('repoId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        ]
        return save_edges

    start = CollectorRestrictedTeam(db=db, org=org, edges=edges_name, query=query,
                                    query_db=query_db, number_of_repo=number_pagination, save_content=content,
                                    save_edges=edges)
    start.start(save_queue_type)
