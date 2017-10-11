import time

import schedule

from collections_and_edges import *
from createDB import create_collections, start_db

db = start_db()
create_collections(db)


def job():
    for org in orgs:
        repo_query(db, org)
        dev(db, org)
        teams(db, org)
        teams_dev(db, org)
        teams_repo(db, org)
        readme(db, org)
        languages(db, org)
        commit_collector(db, org)
        stats_collector(db, org)
        fork_collector(db, org)
        issue(db, org)


job()
schedule.every(update).hour.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
