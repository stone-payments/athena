from collections_edges import *
from collectors_and_savers.saver import SaverThread
from custom_configurations.config import *
from queries.graphql_mongodb_queries import *
from mongodb_connect.mongraph import *

db = Mongraph(db_name, db_url, hash_indexes, hash_indexes_unique, full_text_indexes)
save_queue = Queue(queue_max_size)
save_edges_name_queue = Queue(queue_max_size)
saver = SaverThread(db=db, queue=save_queue, edges_name_queue=save_edges_name_queue)
saver.start()


def job(orgs_list):
    for org in orgs_list:
        org_collection(db, org, org_query, "Org")
        repo(db, org, repo_query, "Repo")
        dev(db, org, dev_query, "Dev")
        teams(db, org, teams_query, "Teams")
        teams_dev(db, org, teams_dev_query, query_teams_dev_mongo, save_queue)
        teams_repo(db, org, teams_repo_query, query_teams_repo_mongo, save_queue)
        commit_collector(db, org, commit_query, query_commit_mongo, "Commit", save_edges_name_queue)
        stats_collector(db, org, stats_query, query_stats_mongo, "Commit", save_edges_name_queue)
        fork_collector(db, org, fork_query, query_fork_mongo, "Fork", save_edges_name_queue)
        issue(db, org, issue_query, issue_mongo, "Issue", save_edges_name_queue)


while True:
    start_time = time.time()
    job(orgs)
    print("--- %s seconds ---" % (time.time() - start_time))
