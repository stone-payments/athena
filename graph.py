from collections_and_edges import *
from createDB import create_collections, start_db
import time
import schedule
db = start_db()
create_collections(db)


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
        # languages(db, org)
        commit_collector(db, org)
        stats_collector(db, org)
        fork_collector(db, org)
        issue(db, org)


start_time = time.time()
job()
print("--- %s seconds ---" % (time.time() - start_time))

# schedule.every(update).hour.do(job)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
