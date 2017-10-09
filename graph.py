import time

import schedule

from collections_and_edges import *
from module import createcollections

db = start_db()
createcollections(db)


def job():
    for org in orgs:
        repoquery(db, org)
        dev(db, org)
        teams(db, org)
        teamsDev(db, org)
        teamsRepo(db, org)
        readme(db, org)
        languages(db, org)
        commitcollector(db, org)
        statscollector(db, org)
        forkcollector(db, org)
        issue(db, org)


job()

schedule.every(update).hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
