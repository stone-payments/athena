from apistar import Route, Response, http
from apistar.frameworks.wsgi import WSGIApp as App

from client import main_api


def hook(request: http.Request, data: http.RequestData):
    event = dict(request.headers)['x-github-event']
    status, headers = github_event(event, data)
    if status:
        return Response({}, status=202, headers=headers)
    else:
        return Response({}, status=500, headers=headers)


def github_event(event, data):
    api = main_api()
    headers = {}
    if event == 'ping':
        headers['x-stone-event'] = 'pong'
        return True, headers
    elif event == 'repository':
        if data['action'] == 'created':
            url = api.get_url('teams', '1014173', 'repos', 'stone-payments', data['repository']['name'], '?permission=pull')
            r = api.put(url)
            headers['x-stone-event'] = 'repository'
            return True, headers
    else:
        headers['x-stone-event'] = event
        return True, headers


routes = [
    Route('/hook', 'POST', hook),
]

app = App(routes=routes)


if __name__ == '__main__':
    app.main()