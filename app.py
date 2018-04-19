from queue import Queue
from threading import Thread

from collection_modules.log_message import log
from collections_edges import OrgCollection, Repo, Dev, Teams, TeamsRepo, TeamsDev, Commit, Fork, Issue
from collectors_and_savers.saver import SaverThread
from custom_configurations.config import queue_max_size, orgs
from graphql_queries.graphql_queries import *
from mongodb_queries.mongodb_queries import query_commit_mongo, query_fork_mongo, query_teams_dev_mongo, \
    query_teams_repo_mongo, issue_mongo


class Collector:
    def __init__(self, db):
        self.db = db
        self.orgs = orgs

    def __create_queue(self):
        self.save_queue = Queue(queue_max_size)
        self.save_edges_name_queue = Queue(queue_max_size)

    def __start_savers(self):
        saver = SaverThread(db=self.db, queue=self.save_queue, edges_name_queue=self.save_edges_name_queue)
        saver.start()

    def __collect(self):
        for org in self.orgs:
            log.info(org + " Org")
            OrgCollection(self.db , org, org_query, "Org").collect()
            log.info(org + " Repo")
            Repo(self.db , org, repo_query, "Repo").collect()
            log.info(org + " Dev")
            Dev(self.db , org, dev_query, "Dev").collect()
            log.info(org + " Teams")
            Teams(self.db , org, teams_query, "Teams").collect()
            log.info(org + " Teams_dev")
            TeamsDev(self.db , org, teams_dev_query, query_teams_dev_mongo, self.save_queue).collect()
            log.info(org + " Teams_repo")
            TeamsRepo(self.db , org, teams_repo_query, query_teams_repo_mongo, self.save_queue).collect()
            log.info(org + " Commit")
            Commit(self.db , org, commit_query, query_commit_mongo, "Commit", self.save_edges_name_queue).collect()
            log.info(org + " fork")
            Fork(self.db , org, fork_query, query_fork_mongo, "Fork", self.save_edges_name_queue).collect()
            log.info(org + " issue")
            Issue(self.db , org, issue_query, issue_mongo, "Issue", self.save_edges_name_queue).collect()

    def __start_collector(self):
        self.__create_queue()
        self.__start_savers()
        self.__collect()

    def start_collector_thread(self):
        workers = [Thread(target=self.__start_collector, args=()) for _ in range(1)]
        [t.start() for t in workers]
