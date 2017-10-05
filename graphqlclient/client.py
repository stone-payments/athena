import json

import requests


class GraphQLClient:
    def __init__(self, endpoint, token, timeout=100.001):
        self.endpoint = endpoint
        self.token = token
        self.timeout = timeout

    def execute(self, query, variables):
        data = {'query': query,
                'variables': variables}
        if self.token != "":
            headers = {'Authorization': 'bearer %s' % self.token}
            req = requests.post(self.endpoint, json.dumps(data), headers=headers, timeout=self.timeout)
            return req.json()
        else:
            raise NameError("Token is not Defined")

class ClientRest:
    def __init__(self, token, timeout=100.001):
        self.token = token
        self.timeout = timeout

    def execute(self, url, query, temp):
        query = url + query + temp
        if self.token != "":
            headers = {'Authorization': 'token %s' % self.token}
            req = requests.get(query, headers=headers, timeout=100.001)
            # print(req)
            return req.json()
        else:
            raise NameError("Token is not Defined")
