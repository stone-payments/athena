from collections_edges import *
from create_db import create_database_if_not_exists, create_collection_if_not_exists
from config import *
from graphql_mongodb_queries import *
import time
from saver import SaverThread

db = create_database_if_not_exists(db_name=db_name, db_url=db_url)
create_collection_if_not_exists(db, hash_indexes, hash_indexes_unique,
                                full_text_indexes)
save_queue = Queue(queue_max_size)
saver = SaverThread(db=db, queue=save_queue, edges_name_queue=save_edges_name_queue)
saver.start()


def job(orgs_list):
    for org in orgs_list:
        org_collection(db, org, org_query, "Org")
        repo(db, org, repo_query, "Repo")
        dev(db, org, dev_query, "Dev")
        teams(db, org, teams_query, "Teams")
        teams_dev(db, org, teams_dev_query, query_teams_dev_mongo)
        teams_repo(db, org, teams_repo_query, query_teams_repo_mongo)
        commit_collector(db, org, commit_query, query_commit_mongo, "Commit")
        stats_collector(db, org, stats_query, query_stats_mongo, "Commit")
        fork_collector(db, org, fork_query, query_fork_mongo, "Fork")
        issue(db, org, issue_query, issue_mongo, "Issue")


while True:
    start_time = time.time()
    job(orgs)
    print("--- %s seconds ---" % (time.time() - start_time))
