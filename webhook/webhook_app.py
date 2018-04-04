from apistar import Route, Response, http
from apistar.frameworks.wsgi import WSGIApp as Webhook
from queue import Queue
from webhook.webhook_event_router import WebhookEventRouter

webhook_queue = Queue(10000)
event_router = WebhookEventRouter(webhook_queue)
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
