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
        # teams2(db, org, teams_query, ["Teams"], "edges")
        # teams_dev(db, org, teams_dev_arango, teams_dev_query)
        # teams_repo(db, org, teams_repo_arango, teams_repo_query)
        # readme(db, org, readme_arango, readme_query)
        commit_collector2(db, org, commit_query, commit_arango, "Commit", "edges")
        # commit_collector(db, org, commit_arango, commit_query)
        # stats_collector(db, org, stats_query)
        # fork_collector(db, org, fork_arango, fork_query)
        # issue(db, org, issue_arango, issue_query)


while True:
    start_time = time.time()
    job(orgs)
    print("--- %s seconds ---" % (time.time() - start_time))

