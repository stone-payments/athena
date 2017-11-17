from collector import *


# TEAMS_DEV ###############################

def teams_dev2(db, org, query, query_db, edges_name="edges"):
    def content(self, response, node):
        save_content = {
        }
        return save_content

    def edges(response, node):
        save_edges = [{
            "edge_name": "dev_to_team",
            'to': find('teamId', response),
            'from': find('memberId', node),
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        }
        ]
        return save_edges

    start = CollectorThread(db=db, org=org, edges=edges_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(team_dev=True)


# TEAMS_REPO ###############################

def teams_repo2(db, org, query, query_db, edges_name="edges"):
    def content(self, response, node):
        save_content = {
        }
        return save_content

    def edges(response, node):
        save_edges = [{
            "edge_name": "dev_to_repo",
            'to': find('teamId', response),
            'from': find('repoId', node),
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        }
        ]
        return save_edges

    start = CollectorThread(db=db, org=org, edges=edges_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(team_dev=True)
