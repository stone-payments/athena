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
        self.edges = edges
        self.since = since
        self.until = until
        self.number_of_repo = number_of_repo
        self.slug = slug
        self.next_repo = next_repo
        self.collection_name = collection_name
        self.save_content = save_content
        self.save_edges = save_edges

    def _save2(self, save):
        c = save
        print(c)
        mongo_test = Mongraph(db=self.db)
        mongo_test.update(obj={"_id": c["_id"]}, patch=c, kind=c["collection_name"])
        for edge in self.save_edges(c):
            # print(edge)
            mongo_test.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                               data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                              'edge_name']})

    def _save(self, collection_name, id_content, save_content):
        self.db[collection_name].update_one(
            id_content,
            {
                "$set": save_content
            },
            upsert=True,
        )

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
            edges = find(self.edges, response)
            for node in edges:
                # print(node)
                queue_input = self.save_content(self, response, node)
                self._save2(queue_input)

    def collect(self):
        has_next_page = True
        cursor = None
        while has_next_page:
            response = pagination_universal(self.query, number_of_repo=self.number_of_repo, next_cursor=cursor,
                                            org=self.org, since=since_time, until=until_time, slug=self.slug,
                                            next_repo=self.next_repo)
            limit_validation(rate_limit=find('rateLimit', response))
            has_next_page = find('hasNextPage', response)
            cursor = find('endCursor', response)
            edges = find(self.edges, response)
            for node in edges:
                for collection in range(0, len(self.collection_name)):
                    self._save(collection_name=self.collection_name[collection],
                               id_content=self.id_content(node)[collection],
                               save_content=self.save_content(node, self.org)[collection])

    def start(self):
        save_queue = Queue(queue_max_size)
        self._collect(save=save_queue)


class CollectorThread:
    def __init__(self, db: object, collection_name: object, org: object, edges: object, query: object, query_db: object,
                 save_content: type, save_edges: type = None, number_of_repo: object = None, slug: object = None,
                 since: object = None, until: object = None):
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
            c = save.get(timeout=commit_queue_timeout)
            mongo_test = Mongraph(db=self.db)
            mongo_test.update(obj={"_id": c["_id"]}, patch=c, kind=c["collection_name"])
            for edge in self.save_edges(c):
                print(edge)
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
                limit_validation(rate_limit=find('rateLimit', response), output=save)
                has_next_page = find('hasNextPage', response)
                cursor = find('endCursor', response)
                edges = find(self.edges, response)
                for node in edges:
                    print(node)
                    queue_input = self.save_content(self, response, node)
                    save.put(queue_input)

    def _query_db(self):
        dictionary = [dict(x) for x in self.db.Repo.find(eval(self.query_db), {'repoName': 1, '_id': 0})]
        query_list = []
        [query_list.append(str(value["repoName"])) for value in dictionary]
        return query_list

    def _start_threads(self):
        repositories_queue = Queue(queue_max_size)
        save_queue = Queue(queue_max_size)
        query_result = self._query_db()
        workers = [Thread(target=self._collect, args=(repositories_queue, save_queue)) for _ in range(num_of_threads)]
        workers2 = [Thread(target=self._save, args=(save_queue,)) for _ in range(num_of_threads)]
        for repo in query_result:
            repositories_queue.put(str(repo))
        [t.start() for t in workers]
        [t.start() for t in workers2]
        [t.join() for t in workers]
        [t.join() for t in workers2]

    def start(self):
        self._start_threads()
