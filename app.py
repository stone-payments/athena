from collections_edges import *
from collectors_and_savers.saver import SaverThread
from custom_configurations.config import *
from graphql_queries.graphql_queries import *
from mongodb_queries.mongodb_queries import *
from mongodb_connect.mongraph import *
from collection_modules.log_message import *

db = Mongraph(db_name=db_name, db_url=db_url, username=username, password=password, auth_mechanism=auth_mechanism,
              hash_indexes=hash_indexes, hash_indexes_unique=hash_indexes_unique,
              full_text_indexes=full_text_indexes)
save_queue = Queue(queue_max_size)
save_edges_name_queue = Queue(queue_max_size)
saver = SaverThread(db=db, queue=save_queue, edges_name_queue=save_edges_name_queue)
saver.start()


def job(orgs_list):
    for org in orgs_list:
        log.info(org + " Org")
        org_collection(db, org, org_query, "Org")
        log.info(org + " Repo")
        repo(db, org, repo_query, "Repo")
        log.info(org + " Dev")
        dev(db, org, dev_query, "Dev")
        log.info(org + " Teams")
        teams(db, org, teams_query, "Teams")
        log.info(org + " Teams_dev")
        teams_dev(db, org, teams_dev_query, query_teams_dev_mongo, save_queue)
        log.info(org + " Teams_repo")
        teams_repo(db, org, teams_repo_query, query_teams_repo_mongo, save_queue)
        log.info(org + " Commit")
        commit_collector(db, org, commit_query, query_commit_mongo, "Commit", save_edges_name_queue)
        log.info(org + " fork")
        fork_collector(db, org, fork_query, query_fork_mongo, "Fork", save_edges_name_queue)
        log.info(org + " issue")
        issue(db, org, issue_query, issue_mongo, "Issue", save_edges_name_queue)


while True:
    start_time = time.time()
    job(orgs)
    print("--- %s seconds ---" % (time.time() - start_time))
