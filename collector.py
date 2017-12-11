import ast
from module import *
from saver import *
from pagination import Pagination


# from app import save_queue, save_edges_name_queue
# from config import save_queue


def _start(query_result: iter, collect_type: object, queue_type: Queue):
    repositories_queue = Queue(queue_max_size)
    workers = [Thread(target=collect_type, args=(repositories_queue, queue_type)) for _ in range(num_of_threads)]
    for repo in query_result:
        repositories_queue.put(str(repo))
    [t.start() for t in workers]
    [t.join() for t in workers]


class Collector:
    def __init__(self, db: object, collection_name: object, org: str, edges: object, query: object,
                 save_content: callable, save_edges: callable, number_of_repo: int = None,
                 next_repo: str = None, slug: str = None, updated_utc_time: callable = utc_time):
        self.db = db
        self.org = org
        self.query = query
        self.edges_name = edges
        self.time = updated_utc_time
        self.number_of_repo = number_of_repo
        self.slug = slug
        self.next_repo = next_repo
        self.collection_name = collection_name
        self.save_content = save_content
        self.save_edges = save_edges


class CollectorTeam(Collector):

    def _collect_team(self):
        return_pagination = Pagination(org=self.org, query=self.query, updated_time=self.time,
                                       number_of_repo=self.number_of_repo, slug=self.slug, next_repo=self.next_repo)
        for page in return_pagination:
            edges = find_key(self.edges_name, page)
            if edges is not None:
                for node in edges:
                    team = self.save_content(self, edges, node)
                    members, repositories = self.save_edges(team, find_key('members_edge', node),
                                                            find_key('repo_edge', node))
                    save = SaverTeam(db=self.db)
                    save.save(team, members, repositories)

    def start(self):
        self._collect_team()


class CollectorGeneric(Collector):
    def _collect(self):
        pagination = Pagination(org=self.org, query=self.query, updated_time=self.time,
                                number_of_repo=self.number_of_repo, slug=self.slug, next_repo=self.next_repo)
        for page in pagination:
            edges = find_key(self.edges_name, page)
            if edges is not None:
                for node in edges:
                    print(node)
                    queue_input = self.save_content(self, page, node)
                    save = SaverGeneric(db=self.db)
                    save.save(queue_input, pagination, save_edges=self.save_edges)
            else:
                queue_input = self.save_content(self, page)
                save = SaverGeneric(db=self.db)
                save.save(queue_input, pagination, save_edges=self.save_edges)

    def start(self):
        self._collect()


class CollectorRestrictedItems:
    def __init__(self, db: object, org: str, collection_name: str = None, edges: str = "edges",
                 query: callable = None, query_db: callable = None, save_content: callable = None,
                 save_edges: callable = None, number_of_repo: int = None, slug: str = None,
                 updated_utc_time: callable = utc_time):
        self.db = db
        self.org = org
        self.query = query
        self.query_db = query_db
        self.edges = edges
        self.time = updated_utc_time
        self.number_of_repo = number_of_repo
        self.slug = slug
        self.collection_name = collection_name
        self.save_content = save_content
        self.save_edges = save_edges

        # @staticmethod
        # def _start(query_result: iter, collect_type: object, queue_type: Queue):
        #     repositories_queue = Queue(queue_max_size)
        #     workers = [Thread(target=collect_type, args=(repositories_queue, queue_type)) for _ in range(num_of_threads)]
        #     for repo in query_result:
        #         repositories_queue.put(str(repo))
        #     [t.start() for t in workers]
        #     [t.join() for t in workers]


class CollectorRestricted(CollectorRestrictedItems):
    def _collect(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            return_pagination = Pagination(query=self.query, number_of_repo=self.number_of_repo, org=self.org,
                                           updated_time=self.time, slug=self.slug, next_repo=repository)
            for page in return_pagination:
                print(page)
                edges = find_key(self.edges, page)
                if edges is not None:
                    for node in edges:
                        queue_input = (self.save_content(self, page, node), self.save_edges)
                        save.put(queue_input)

    def start(self, save_edges_name_queue):
        query_result = self.query_db(self)
        _start(query_result, self._collect, save_edges_name_queue)


class CollectorStats(CollectorRestrictedItems):
    def _collect_commit_stats(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            repository = ast.literal_eval(repository)
            rest_query = self.query(self, repository)
            result = client_rest.execute(url_rest_api, rest_query, str(repository['oid']))
            time.sleep(abuse_time_sleep)
            queue_input = (self.save_content(result, repository["_id"]), self.save_edges)
            save.put(queue_input)

    def start(self, save_edges_name_queue):
        query_result = self.query_db(self)
        _start(query_result, self._collect_commit_stats, save_edges_name_queue)


class CollectorRestrictedTeam(CollectorRestrictedItems):
    def _collect_team_dev(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            return_pagination = Pagination(query=self.query, number_of_repo=self.number_of_repo, org=self.org,
                                           updated_time=self.time, slug=repository)
            for page in return_pagination:
                edges = find_key(self.edges, page)
                if edges is not None:
                    for node in edges:
                        print(node)
                        queue_input = self.save_edges(page, node)
                        save.put(queue_input)

    def start(self, save_queue):
        query_result = self.query_db(self)
        _start(query_result, self._collect_team_dev, save_queue)
