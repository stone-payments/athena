from queue import Queue
from threading import Thread

from collection_modules.validators import validate_edge
from custom_configurations.config import num_of_threads


class Saver:
    def __init__(self, db: callable, queue: Queue = None, edges_name_queue: Queue = None):
        self.db = db
        self.save_queue = queue
        self.save_edges_name_queue = edges_name_queue


class SaverGeneric(Saver):
    def save(self, save: dict, response: object, save_edges: type):
        self.db.update(obj={"_id": save["_id"]}, patch=save, kind=save["collection_name"])
        edges = save_edges(save, response)
        edges = [edge for edge in edges if validate_edge(edge.get("to"), edge.get("from"), edge.get("edge_name"))]
        for edge in edges:
            self.db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                            data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                           'edge_name']})


class SaverTeam(Saver):
    def save(self, team, members, repos):
        self.db.update(obj={"_id": team["_id"]}, patch=team, kind=team["collection_name"])
        members = [member for member in members if validate_edge(member.get("to"), member.get("from"),
                                                                 member.get("edge_name"))]
        repos = [repo for repo in repos if validate_edge(repo.get("to"), repo.get("from"),
                                                         repo.get("edge_name"))]
        for member in members:
            self.db.connect(to=member.get("to"), from_=member.get("from"), kind=member.get("edge_name"),
                            data={key: value for key, value in member.items() if key not in ['from', 'to',
                                                                                             'edge_name']})
        for repo in repos:
            self.db.connect(to=repo.get("to"), from_=repo.get("from"), kind=repo.get("edge_name"),
                            data={key: value for key, value in repo.items() if key not in ['from', 'to',
                                                                                           'edge_name']})


class SaverThread(Saver):
    def save_from_queue(self):
        while True:
            returned_data = self.save_edges_name_queue.get(block=True)
            save_data = returned_data[0]
            save_edges = returned_data[1]
            self.db.update(obj={"_id": save_data["_id"]}, patch=save_data, kind=save_data["collection_name"])
            edges = [edge for edge in save_edges(save_data) if validate_edge(edge.get("to"), edge.get("from"),
                                                                             edge.get("edge_name"))]
            for edge in edges:
                self.db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                                data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                               'edge_name']})

    def save_edges(self):
        while True:
            save_edges = self.save_queue.get(block=True)
            save_edges = [edge for edge in save_edges if validate_edge(edge.get("to"), edge.get("from"),
                                                                       edge.get("edge_name"))]
            for edge in save_edges:
                self.db.connect(to=edge.get("to"), from_=edge.get("from"), kind=edge.get("edge_name"),
                                data={key: value for key, value in edge.items() if key not in ['from', 'to',
                                                                                               'edge_name']})

    def start(self):
        workers = [Thread(target=self.save_from_queue, args=()) for _ in range(num_of_threads)]
        workers2 = [Thread(target=self.save_edges, args=()) for _ in range(num_of_threads)]
        [t.start() for t in workers]
        [t.start() for t in workers2]
