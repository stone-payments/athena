from apistar import Route, Response, http
from apistar.frameworks.wsgi import WSGIApp as Webhook
import pprint
from collection_modules.module import find_key
from webhook.webhook_get_commit import GetCommit


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

    elif event == 'push' and find_key("deleted", data) is False:
        pprint.pprint(data)
        get_commit = GetCommit()
        get_commit.get_data(data)
        headers['x-stone-event'] = 'push'
        return True, headers
    else:
        headers['x-stone-event'] = event
        return True, headers


routes = [
    Route('/hook', 'POST', hook),
]

app = Webhook(routes=routes)


if __name__ == '__main__':
    app.main()
