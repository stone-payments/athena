import ast
from module import *
from saver import *
from pagination import Pagination


class Collector:
    def __init__(self, db: object, collection_name: object, org: object, edges: object, query: object,
                 save_content: type, save_edges: type, number_of_repo: object = None,
                 next_repo: object = None, slug: object = None, since: type = since_time, until: type = until_time):
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


class CollectorTeam(Collector):

    def _collect_team(self):
        return_pagination = Pagination(org=self.org, query=self.query, since=self.since, until=self.until,
                                       number_of_repo=self.number_of_repo, slug=self.slug, next_repo=self.next_repo)
        for page in return_pagination:
            edges = find(self.edges_name, page)
            if edges is not None:
                for node in edges:
                    team = self.save_content(self, edges, node)
                    members, repositories = self.save_edges(team, find('members_edge', node),
                                                            find('repo_edge', node))
                    save = SaverTeam(db=self.db)
                    save.save(team, members, repositories)

    def start(self):
        self._collect_team()


class CollectorGeneric(Collector):
    def _collect(self):
        pagination = Pagination(org=self.org, query=self.query, since=self.since, until=self.until,
                                number_of_repo=self.number_of_repo, slug=self.slug, next_repo=self.next_repo)
        for page in pagination:
            edges = find(self.edges_name, page)
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
    def __init__(self, db: object, collection_name: object = None, org: object = None, edges: object = "edges",
                 query: type = None, query_db: type = None, save_content: type = None, save_edges: type = None,
                 number_of_repo: object = None, slug: object = None, since: type = since_time,
                 until: type = until_time):
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

    @staticmethod
    def _start(query_result: iter, collect_type: object, queue_type: Queue):
        repositories_queue = Queue(queue_max_size)
        workers = [Thread(target=collect_type, args=(repositories_queue, queue_type)) for _ in range(num_of_threads)]
        for repo in query_result:
            repositories_queue.put(str(repo))
        [t.start() for t in workers]
        [t.join() for t in workers]


class CollectorRestricted(CollectorRestrictedItems):
    def _collect(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            return_pagination = Pagination(query=self.query, number_of_repo=self.number_of_repo, org=self.org,
                                           since=self.since, until=self.until, slug=self.slug, next_repo=repository)
            for page in return_pagination:
                edges = find(self.edges, page)
                if edges is not None:
                    for node in edges:
                        queue_input = (self.save_content(self, page, node), self.save_edges)
                        save.put(queue_input)

    def start(self):
        query_result = self.query_db(self)
        super()._start(query_result, self._collect, save_edges_name_queue)


class CollectorStats(CollectorRestrictedItems):
    def _collect_commit_stats(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            repository = ast.literal_eval(repository)
            rest_query = self.query(self, repository)
            result = clientRest2.execute(url_rest_api, rest_query, str(repository['oid']))
            time.sleep(abuse_time_sleep)
            queue_input = (self.save_content(result, repository["_id"]), self.save_edges)
            save.put(queue_input)

    def start(self):
        query_result = self.query_db(self)
        super()._start(query_result, self._collect_commit_stats, save_edges_name_queue)


class CollectorRestrictedTeam(CollectorRestrictedItems):
    def _collect_team_dev(self, repositories: Queue, save: Queue):
        while True:
            repository = repositories.get(timeout=queue_timeout)
            return_pagination = Pagination(query=self.query, number_of_repo=self.number_of_repo, org=self.org,
                                           since=self.since, until=self.until, slug=repository)
            for page in return_pagination:
                edges = find(self.edges, page)
                if edges is not None:
                    for node in edges:
                        print(node)
                        queue_input = self.save_edges(page, node)
                        save.put(queue_input)

    def start(self):
        query_result = self.query_db(self)
        super()._start(query_result, self._collect_team_dev, save_queue)
