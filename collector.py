from queue import Queue
from mongraph import *
import ast
from module import *
from threading import Thread
from validators import *


class Iter:
    def __init__(self,
                 query,
                 number_of_repo=None,
                 next_cursor=None,
                 next_repo=None,
                 org=None,
                 slug=None,
                 since=None,
                 until=None):

        self.query = query
        self.number_of_repo = number_of_repo
        self.next_cursor = next_cursor
        self.next_repo = next_repo
        self.org = org
        self.slug = slug
        self.since = since
        self.until = until

    def __next__(self):
        if self.__has_next_page():
            yield self.__next_page()
        else:
            raise StopIteration()

    def __has_next_page(self):
        return True

    def __next_page(self):
        pass


# for page in Iter():
#     page


class Save:
    def __init__(self, db):
        self.db = db

    def _save_thread(self, save: Queue):
        while True:
            save_data = save.get(timeout=queue_timeout)
            db = Mongraph(db=self.db)
            db.update(obj={"_id": save_data["_id"]}, patch=save_data, kind=save_data["collection_name"])
            for edge in self.save_edges(save_data):
                if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
                    continue
                db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                           data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                          'edge_name']})

    def _save_edges_thread(self, save: Queue):
        while True:
            save_edges = save.get(timeout=queue_timeout)
            db = Mongraph(db=self.db)
            for edge in save_edges:
                if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
                    continue
                db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                           data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                          'edge_name']})


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
        db = Mongraph(db=self.db)
        db.update(obj={"_id": save["_id"]}, patch=save, kind=save["collection_name"])
        for edge in self.save_edges(save, response):
            if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
                continue
            db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                       data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                      'edge_name']})

    def _save_team(self, team, members, repos):
        db = Mongraph(db=self.db)
        db.update(obj={"_id": team["_id"]}, patch=team, kind=team["collection_name"])
        for member in members:
            if validate_edge(member.get("to"), member.get("from"), member.get("edge_name")):
                continue
            db.connect(to=member.get("to"), from_=member.get("from"), kind=member.get("edge_name"),
                       data={key: value for key, value in member.items() if key not in ['from', 'to',
                                                                                        'edge_name']})
        for repo in repos:
            if validate_edge(repo.get("to"), repo.get("from"), repo.get("edge_name")):
                continue
            db.connect(to=repo.get("to"), from_=repo.get("from"), kind=repo.get("edge_name"),
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

    def _save_thread(self, save: Queue):
        while True:
            save_data = save.get(timeout=queue_timeout)
            db = Mongraph(db=self.db)
            db.update(obj={"_id": save_data["_id"]}, patch=save_data, kind=save_data["collection_name"])
            for edge in self.save_edges(save_data):
                if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
                    continue
                db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                           data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                          'edge_name']})

    def _save_edges_thread(self, save: Queue):
        while True:
            save_edges = save.get(timeout=queue_timeout)
            db = Mongraph(db=self.db)
            for edge in save_edges:
                if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
                    continue
                db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                           data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                          'edge_name']})

    def _collect_thread(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
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

    def _collect_commit_stats_thread(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            repository = ast.literal_eval(repository)
            rest_query = self.query(self, repository)
            result = clientRest2.execute(url_rest_api, rest_query, str(repository['oid']))
            queue_input = self.save_content(result, repository["_id"])
            print(queue_input)
            save.put(queue_input)

    def _collect_team_dev_thread(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
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
            self._start_threads(query_result, self._collect_commit_stats_thread, self._save_thread)
        elif team_dev is True:
            self._start_threads(query_result, self._collect_team_dev_thread, self._save_edges_thread)
        else:
            self._start_threads(query_result, self._collect_thread, self._save_thread)


class Collector:
    def __init__(self, db: object, collection_name: object = None, org: object = None, edges: object = 'edges',
                 query: object = None,
                 query_db: type = None, save_content: type = None, save_edges: type = None,
                 number_of_repo: object = None,
                 next_repo: object = None, slug: object = None, since: object = None, until: object = None):

        self.db = db
        self.org = org
        self.query = query
        self.query_db = query_db
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
        db = Mongraph(db=self.db)
        db.update(obj={"_id": save["_id"]}, patch=save, kind=save["collection_name"])
        for edge in self.save_edges(save, response):
            if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
                continue
            db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                       data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                      'edge_name']})

    def _save_team(self, team, members, repos):
        db = Mongraph(db=self.db)
        db.update(obj={"_id": team["_id"]}, patch=team, kind=team["collection_name"])
        for member in members:
            if validate_edge(member.get("to"), member.get("from"), member.get("edge_name")):
                continue
            db.connect(to=member.get("to"), from_=member.get("from"), kind=member.get("edge_name"),
                       data={key: value for key, value in member.items() if key not in ['from', 'to',
                                                                                        'edge_name']})
        for repo in repos:
            if validate_edge(repo.get("to"), repo.get("from"), repo.get("edge_name")):
                continue
            db.connect(to=repo.get("to"), from_=repo.get("from"), kind=repo.get("edge_name"),
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

    # def _save_thread(self, save: Queue):
    #     while True:
    #         save_data = save.get(timeout=queue_timeout)
    #         db = Mongraph(db=self.db)
    #         db.update(obj={"_id": save_data["_id"]}, patch=save_data, kind=save_data["collection_name"])
    #         for edge in self.save_edges(save_data):
    #             if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
    #                 continue
    #             db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
    #                        data={key: value for key, value in edge.items() if key not in ['from', 'to',
    #                                                                                       'edge_name']})
    #
    # def _save_edges_thread(self, save: Queue):
    #     while True:
    #         save_edges = save.get(timeout=queue_timeout)
    #         db = Mongraph(db=self.db)
    #         for edge in save_edges:
    #             if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name")):
    #                 continue
    #             db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
    #                        data={key: value for key, value in edge.items() if key not in ['from', 'to',
    #                                                                                       'edge_name']})

    def _collect_thread(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
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
                edges = find(self.edges_name, response)
                for node in edges:
                    queue_input = (self.save_edges, self.save_content(self, response, node))
                    save.put(queue_input)

    def _collect_commit_stats_thread(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            repository = ast.literal_eval(repository)
            rest_query = self.query(self, repository)
            result = clientRest2.execute(url_rest_api, rest_query, str(repository['oid']))
            queue_input = self.save_content(result, repository["_id"])
            print(queue_input)
            save.put(queue_input)

    def _collect_team_dev_thread(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
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
                edges = find(self.edges_name, response)
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

    def start(self, thread=False, stats=False, team=False, team_dev=False):
        # if thread:
        #     query_result = self.query_db(self)
        if stats and thread:
            self._start_threads(self.query_db(self), self._collect_commit_stats_thread, self._save_thread)
        elif team_dev and thread:
            self._start_threads(self.query_db(self), self._collect_team_dev_thread, self._save_edges_thread)
        elif thread:
            self._start_threads(self.query_db(self), self._collect_thread, self._save_thread)
        elif team:
            save_queue = Queue(queue_max_size)
            self._collect_team(save=save_queue)
        else:
            save_queue = Queue(queue_max_size)
            self._collect(save=save_queue)
