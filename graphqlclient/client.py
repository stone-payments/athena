import json

import requests


class GraphQLClient:
    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.token = token

    def execute(self, query, variables):
        return self._send(query, variables)

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}

        if self.token is not None:
            headers = {'Authorization': 'bearer %s' % self.token}
            req = requests.post(self.endpoint, json.dumps(data), headers=headers, timeout=100.001)
            return req.json()
