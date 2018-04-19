
from queue import Queue

from apistar import Route, Response, http
from apistar.frameworks.wsgi import WSGIApp as Webhook

from custom_configurations.config import db_name, db_url, username, password, mongo_port, hash_indexes, \
    hash_indexes_unique, full_text_indexes, auth_source
from mongodb_connect.db_connection import DbConnection
from mongodb_connect.mongraph import Mongraph
from webhook.webhook_event_router import WebhookEventRouter

db_connection = DbConnection(db_name=db_name, db_url=db_url, username=username, password=password, mongo_port=mongo_port,
                             hash_indexes=hash_indexes, hash_indexes_unique=hash_indexes_unique,
                             full_text_indexes=full_text_indexes, auth_source=auth_source).create_db()
db = Mongraph(db=db_connection)

webhook_queue = Queue(10000)
event_router = WebhookEventRouter(db, webhook_queue)
event_router.start()


def hook(request: http.Request, data: http.RequestData):
    event = dict(request.headers)['x-github-event']
    status, headers = github_event(event, data)
    if status:
        return Response({}, status=202, headers=headers)
    else:
        return Response({}, status=500, headers=headers)


def github_event(event, data):
    headers = {}
    if event == 'ping':
        headers['x-stone-event'] = 'pong'
        return True, headers
    else:
        webhook_queue.put([event, data])
        headers['x-stone-event'] = event
        return True, headers


routes = [
    Route('/hook', 'POST', hook),
]

app = Webhook(routes=routes)


if __name__ == '__main__':
    app.main()


