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

    def execute(self, url: object, query: object, temp: object) -> object:
        query = url + query + temp
        if self.token != "":
            headers = {'Authorization': 'token %s' % self.token}
            req = requests.get(query, headers=headers, timeout=self.timeout)
            return req.json()
        else:
            raise NameError("Token is not Defined")

#
# clientRest2 = ClientRest("896a853e110a21a6e25cbbcf1ebd2e2ce1139a8e")
# print(clientRest2.execute(url='https://api.github.com/rate_limit', query='', temp=''))
# /repos/:owner/:repo/events
