from collections_edges import *
from collectors_and_savers.saver import SaverThread
from custom_configurations.config import *
from graphql_queries.graphql_queries import *
from mongodb_queries.mongodb_queries import *
from mongodb_connect.mongraph import *
from mongodb_connect.db_connection import DbConnection
from collection_modules.log_message import *

db_connection = DbConnection(db_name=db_name, db_url=db_url, username=username, password=password, mongo_port=mongo_port,
                             hash_indexes=hash_indexes, hash_indexes_unique=hash_indexes_unique,
                             full_text_indexes=full_text_indexes).create_db()
db = Mongraph(db=db_connection)
save_queue = Queue(queue_max_size)
save_edges_name_queue = Queue(queue_max_size)
saver = SaverThread(db=db, queue=save_queue, edges_name_queue=save_edges_name_queue)
saver.start()


def job(orgs_list):
    for org in orgs_list:
        log.info(org + " Org")
        OrgCollection(db, org, org_query, "Org").collect()
        log.info(org + " Repo")
        Repo(db, org, repo_query, "Repo").collect()
        log.info(org + " Dev")
        Dev(db, org, dev_query, "Dev").collect()
        log.info(org + " Teams")
        Teams(db, org, teams_query, "Teams").collect()
        log.info(org + " Teams_dev")
        TeamsDev(db, org, teams_dev_query, query_teams_dev_mongo, save_queue).collect()
        log.info(org + " Teams_repo")
        TeamsRepo(db, org, teams_repo_query, query_teams_repo_mongo, save_queue).collect()
        log.info(org + " Commit")
        Commit(db, org, commit_query, query_commit_mongo, "Commit", save_edges_name_queue).collect()
        log.info(org + " fork")
        Fork(db, org, fork_query, query_fork_mongo, "Fork", save_edges_name_queue).collect()
        log.info(org + " issue")
        Issue(db, org, issue_query, issue_mongo, "Issue", save_edges_name_queue).collect()


while True:
    job(orgs)
