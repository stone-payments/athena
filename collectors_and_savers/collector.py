import ast
import queue
from collection_modules.module import *
from collection_modules.pagination import Pagination
from collectors_and_savers.saver import *


def _start_repository_queue_worker(query_result: iter, collect_type: object, queue_type: Queue):
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

    def _collect(self):
        return_pagination = Pagination(org=self.org, query=self.query, updated_time=self.time,
                                       number_of_repo=self.number_of_repo, slug=self.slug, next_repo=self.next_repo)
        for page in return_pagination:
            edges = find_key(self.edges_name, page)
            self.process_edges(edges, return_pagination=return_pagination, page=page)

    def process_edges(self, edges, **kwargs): pass

    def start(self):
        self._collect()


class CollectorTeam(Collector):
    def process_edges(self, edges, **kwargs):
        if edges is not None:
            for node in edges:
                team = self.save_content(edges=edges, node=node)
                members, repositories = self.save_edges(content=team, members=find_key('members_edge', node),
                                                        repos=find_key('repo_edge', node))
                save = SaverTeam(db=self.db)
                save.save(team, members, repositories)


class CollectorGeneric(Collector):
    def process_edges(self, edges, **kwargs):
        if edges is not None:
            for node in edges:
                queue_input = self.save_content(node=node, org=self.org, page=kwargs.get('page'))
                save = SaverGeneric(db=self.db)
                save.save(queue_input, kwargs.get('return_pagination'), save_edges=self.save_edges)
        else:
            queue_input = self.save_content(org=self.org, page=kwargs.get('page'))
            save = SaverGeneric(db=self.db)
            save.save(queue_input, kwargs.get('return_pagination'), save_edges=self.save_edges)


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

    def _collect(self, repositories: Queue, save: Queue):
        while True:
            try:
                repository = repositories.get_nowait()
                return_pagination = Pagination(query=self.query, number_of_repo=self.number_of_repo, org=self.org,
                                               updated_time=self.time, slug=self.slug, next_repo=repository)
                for page in return_pagination:
                    print(page)
                    edges = find_key(self.edges, page)
                    if edges is not None:
                        for node in edges:
                            self.process_edges(page, node, save)
            except queue.Empty:
                break

    def process_edges(self, page, node, save):
        pass

    def start(self, queue_type):
        query_result = self.query_db(self)
        _start_repository_queue_worker(query_result, self._collect, queue_type)


class CollectorRestricted(CollectorRestrictedItems):
    def process_edges(self, page, node, save: Queue):
        queue_input = (self.save_content(page=page, node=node), self.save_edges)
        save.put(queue_input)


class CollectorCommitStats(CollectorRestrictedItems):
    def _collect(self, repositories: Queue, save: Queue):
        while True:
            try:
                repository = repositories.get_nowait()
                repository = ast.literal_eval(repository)
                rest_query = self.query(self, repository)
                result = client_rest.execute(url_rest_api, rest_query, str(repository['oid']))
                time.sleep(abuse_time_sleep)
                queue_input = (self.save_content(result, repository["_id"]), self.save_edges)
                save.put(queue_input)
            except queue.Empty:
                break


class CollectorRestrictedTeam(CollectorRestrictedItems):
    def process_edges(self, page, node, save: Queue):
        queue_input = self.save_edges(page, node)
        save.put(queue_input)
