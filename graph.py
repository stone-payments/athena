from collections_and_edges import *
from createDB import create_database_if_not_exists
from config import *
from graphql_queries import *

db = create_database_if_not_exists(db_name, db_url, username, password)


# create_collection_if_not_exists(db, collections, hash_indexes, hash_indexes_unique, skip_list_indexes,
#                                 full_text_indexes)


def job(orgs):
    for org in orgs:
        print(org)
        # repo2(db, org, repo_query, ["Repo"], "edges")
        # dev2(db, org, dev_query, ["Dev"], "edges")
        teams2(db, org, query_team_mongo, ["Teams"], "edges")
        # teams_dev2(db, org, teams_dev_query, teams_dev_arango, ["Teams"], "edges")
        # teams_repo(db, org, teams_repo_arango, teams_repo_query)
        # readme(db, org, readme_arango, readme_query)
        # commit_collector2(db, org, commit_query, commit_arango, ["Commit"], "edges")
        # stats_collector2(db, org, stats_query, ["Commit"], "edges")
        # fork_collector2(db, org, fork_query, query_fork_mongo, ["Fork"], "edges")
        # issue2(db, org, issue_query, issue_mongo,  ["Issue"], "edges")


while True:
    start_time = time.time()
    job(orgs)
    print("--- %s seconds ---" % (time.time() - start_time))

