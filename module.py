from threading import Thread
import sys
from datetime import datetime
from pyArango.theExceptions import (UpdateError, CreationError)
from config import *
from graphqlclient import ClientRest
from graphqlclient import GraphQLClient
from classes import *
import time
from queue import Queue
from mongraph import *
import json
import ast

client = GraphQLClient(url, token, timeout)
clientRest2 = ClientRest(token, timeout)


# PAGINATION ###############################


def pagination_universal(query, number_of_repo=None, next_cursor=None, next_repo=None, org=None, slug=None, since=None,
                         until=None):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repo,
                             "next": next_cursor,
                             "next2": next_repo,
                             "org": org,
                             "slug": slug,
                             "sinceTime": since,
                             "untilTime": until
                         })
    return pag


# FIND ###############################


def find(key, json) -> object:
    if isinstance(json, list):
        for item in json:
            f = find(key, item)
            if f is not None:
                return f
    elif isinstance(json, dict):
        if key in json:
            return json[key]
        else:
            for inner in json.values():
                f = find(key, inner)
                if f is not None:
                    return f
    return None


# HANDLING EXCEPTIONS ###############

def handling_except(exception):
    if type(exception) == CreationError or type(exception) == UpdateError or type(exception) == KeyError:
        pass
    else:
        print(exception)
        sys.exit(1)


def limit_validation(rate_limit=None, output=None, readme_limit=None):
    if readme_limit is not None:
        with open("queries/rate_limit_query.aql", "r") as query:
            query = query.read()
        prox = pagination_universal(query)
        return limit_validation(rate_limit=find('rateLimit', prox))
    if rate_limit is not None and rate_limit["remaining"] < rate_limit_to_sleep:
        limit_time = (datetime.datetime.strptime(rate_limit["resetAt"], '%Y-%m-%dT%H:%M:%SZ') -
                      datetime.datetime.utcnow()).total_seconds()
        print("wait " + str(limit_time / 60) + " mins")
        if output is not None:
            return time.sleep(limit_time), output.put(rate_limit)
        elif output is None:
            return time.sleep(limit_time)


def parse_multiple_languages(object_to_be_parsed, edge, key, value):
    dictionary = {}
    try:
        for node in find(edge, object_to_be_parsed):
            dictionary[str((find(key, node)))] = round(((find(value, node) /
                                                         find('totalSize', object_to_be_parsed)) * 100), 2)
        return dictionary
    except Exception:
        return None


class Collector:
    def __init__(self, db, collection_name, org, edges, query, save_content, save_edges, number_of_repo=None,
                 next_repo=None, slug=None, since=None, until=None):
        self.db = db
        self.org = org
        self.query = query
        self.edges_name = edges
        self.since = since
        self.until = until
        self.number_of_repo = number_of_repo
        self.slug = slug
        self.next_repo = next_repo
        self.collection_name = collection_name
        self.save_content = save_content
        self.save_edges = save_edges

    def _save(self, save, response):
        print(save)
        mongo_test = Mongraph(db=self.db)
        mongo_test.update(obj={"_id": save["_id"]}, patch=save, kind=save["collection_name"])
        for edge in self.save_edges(save, response):
            mongo_test.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                               data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                              'edge_name']})

    def _save_team(self, team, members, repos):
        mongo_test = Mongraph(db=self.db)
        mongo_test.update(obj={"_id": team["_id"]}, patch=team, kind=team["collection_name"])
        for member in members:
            mongo_test.connect(to=member.get("to"), from_=member.get("from"), kind=member.get("edge_name"),
                               data={key: value for key, value in member.items() if key not in ['from', 'to',
                                                                                                'edge_name']})
        for repo in repos:
            mongo_test.connect(to=repo.get("to"), from_=repo.get("from"), kind=repo.get("edge_name"),
                               data={key: value for key, value in repo.items() if key not in ['from', 'to',
                                                                                              'edge_name']})

    def _collect(self, save: Queue):
        has_next_page = True
        cursor = None
        print("FOI")
        while has_next_page:
            response = pagination_universal(self.query, number_of_repo=self.number_of_repo, next_cursor=cursor,
                                            org=self.org, since=since_time, until=until_time, slug=self.slug,
                                            next_repo=self.next_repo)
            print(response)

            limit_validation(rate_limit=find('rateLimit', response), output=save)
            has_next_page = find('hasNextPage', response)
            cursor = find('endCursor', response)
            edges = find(self.edges_name, response)
            for node in edges:
                queue_input = self.save_content(self, response, node)
                self._save(queue_input, response)

    def _collect_team(self, save: Queue):
        has_next_page = True
        cursor = None
        print("FOI")
        while has_next_page:
            response = pagination_universal(self.query, number_of_repo=self.number_of_repo, next_cursor=cursor,
                                            org=self.org, since=since_time, until=until_time, slug=self.slug,
                                            next_repo=self.next_repo)
            print(response)
            limit_validation(rate_limit=find('rateLimit', response), output=save)
            has_next_page = find('hasNextPage', response)
            cursor = find('endCursor', response)
            edges = find(self.edges_name, response)
            for node in edges:
                team = self.save_content(self, edges, node)
                members, repositories = self.save_edges(team, find('members_edge', node),
                                                        find('repo_edge', node))
                self._save_team(team, members, repositories)

    def start(self):
        save_queue = Queue(queue_max_size)
        self._collect(save=save_queue)

    def start_team(self):
        save_queue = Queue(queue_max_size)
        self._collect_team(save=save_queue)


class CollectorThread:
    def __init__(self, db: object, collection_name: object = None, org: object = None, edges: object = "edges",
                 query: type = None,
                 query_db: type = None, save_content: type = None, save_edges: type = None,
                 number_of_repo: object = None, slug: object = None, since: object = None, until: object = None):
        self.db = db
        self.org = org
        self.query = query
        self.query_db = query_db
        self.edges = edges
        self.since = since
        self.until = until
        self.number_of_repo = number_of_repo
        self.slug = slug
        self.collection_name = collection_name
        self.save_content = save_content
        self.save_edges = save_edges

    def _save(self, save: Queue):
        while True:
            save_data = save.get(timeout=commit_queue_timeout)
            mongo_test = Mongraph(db=self.db)
            mongo_test.update(obj={"_id": save_data["_id"]}, patch=save_data, kind=save_data["collection_name"])
            for edge in self.save_edges(save_data):
                print(edge)
                mongo_test.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                                   data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                                  'edge_name']})

    def _save_edges(self, save: Queue):
        while True:
            save_edges = save.get(timeout=commit_queue_timeout)
            mongo_test = Mongraph(db=self.db)
            for edge in save_edges:
                mongo_test.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                                   data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                                  'edge_name']})

    def _collect(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=commit_queue_timeout)
            has_next_page = True
            cursor = None
            while has_next_page:
                response = pagination_universal(self.query, number_of_repo=self.number_of_repo, next_cursor=cursor,
                                                org=self.org, since=since_time, until=until_time, slug=self.slug,
                                                next_repo=repository)
                print(response)
                limit_validation(rate_limit=find('rateLimit', response), output=save)
                has_next_page = find('hasNextPage', response)
                cursor = find('endCursor', response)
                edges = find(self.edges, response)

                for node in edges:
                    queue_input = self.save_content(self, response, node)
                    save.put(queue_input)

    def _collect_commit_stats(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=commit_queue_timeout)
            repository = ast.literal_eval(repository)
            rest_query = self.query(self, repository)
            # rest_query = self.org + "/" + str(repository["repoName"]) + '/commits/'
            result = clientRest2.execute(urlCommit, rest_query, str(repository['oid']))
            queue_input = self.save_content(result, repository["_id"])
            print(queue_input)
            save.put(queue_input)

    def _collect_team_dev(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=commit_queue_timeout)
            has_next_page = True
            cursor = None
            print(repository)
            while has_next_page:
                response = pagination_universal(self.query, number_of_repo=self.number_of_repo, next_cursor=cursor,
                                                org=self.org, since=since_time, until=until_time, slug=repository
                                                )
                print(response)
                limit_validation(rate_limit=find('rateLimit', response), output=save)
                has_next_page = find('hasNextPage', response)
                cursor = find('endCursor', response)
                edges = find(self.edges, response)
                for node in edges:
                    queue_input = self.save_edges(response, node)
                    save.put(queue_input)

    @staticmethod
    def _start_threads(query_result, collect_type, save_type):
        repositories_queue = Queue(queue_max_size)
        save_queue = Queue(queue_max_size)
        print(query_result)
        workers = [Thread(target=collect_type, args=(repositories_queue, save_queue)) for _ in range(num_of_threads)]
        workers2 = [Thread(target=save_type, args=(save_queue,)) for _ in range(num_of_threads)]
        for repo in query_result:
            repositories_queue.put(str(repo))
        [t.start() for t in workers]
        [t.start() for t in workers2]
        [t.join() for t in workers]
        [t.join() for t in workers2]

    def start(self, stats=None, team_dev=None):
        query_result = self.query_db(self)
        if stats is True:
            self._start_threads(query_result, self._collect_commit_stats, self._save)
        elif team_dev is True:
            self._start_threads(query_result, self._collect_team_dev, self._save_edges)
        else:
            self._start_threads(query_result, self._collect, self._save)

