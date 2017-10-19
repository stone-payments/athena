from collections_and_edges import *
from createDB import create_database_if_not_exists, create_collection_if_not_exists
from config import *
import time

db = create_database_if_not_exists(db_name, db_url, username, password)
create_collection_if_not_exists(db, collections, hash_indexes, hash_indexes_unique, skip_list_indexes,
                                full_text_indexes)


def job():
    for org in orgs:
        repo_query(db, org)
        with open("queries/devQuery.txt", "r") as query:
            query = query.read()
        dev(db, org, query)
        teams(db, org)
        teams_dev(db, org)
        teams_repo(db, org)
        readme(db, org)
        commit_collector(db, org)
        stats_collector(db, org)
        fork_collector(db, org)
        issue(db, org)


while True:
    start_time = time.time()
    job()
    print("--- %s seconds ---" % (time.time() - start_time))


# schedule.every(update).hour.do(job)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
