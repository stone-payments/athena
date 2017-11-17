from collections_and_edges import *
from createDB import create_database_if_not_exists
from config import *
from graphql_queries import *
from pymongo import IndexModel, ASCENDING, DESCENDING
db = create_database_if_not_exists(db_name, db_url, username, password)


# create_collection_if_not_exists(db, collections, hash_indexes, hash_indexes_unique, skip_list_indexes,
#                                 full_text_indexes)

# index2 = IndexModel([("orgw", DESCENDING)])
# db.Repo.create_indexes([index2])

def job(orgs):
    for org in orgs:
        print(org)
        repo2(db, org, repo_query, ["Repo"])
        dev2(db, org, dev_query, ["Dev"])
        teams2(db, org, teams_query, ["Teams"])
        teams_dev2(db, org, teams_dev_query, query_teams_dev_mongo)
        teams_repo2(db, org, teams_repo_query, query_teams_repo_mongo)
        commit_collector2(db, org, commit_query, query_commit_mongo, ["Commit"])
        stats_collector2(db, org, stats_query, query_stats_mongo, ["Commit"])
        fork_collector2(db, org, fork_query, query_fork_mongo, ["Fork"])
        issue2(db, org, issue_query, issue_mongo, ["Issue"])


while True:
    start_time = time.time()
    job(orgs)
    print("--- %s seconds ---" % (time.time() - start_time))

    # db.getCollection('edges').aggregate([{$lookup: {from: 'Teams', localField: 'to', foreignField: '_id', as: 'Team'}}, {$lookup: {from: 'Dev', localField: 'from', foreignField: '_id', as: 'Dev'}},
    # {
    #   $match:
    # {"Team.0.slug":'plataforma'}
    # }
    # ])
