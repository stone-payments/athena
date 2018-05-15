import json
import os
import re
import requests


class ClientRest(object):

    def __init__(self, token):
        self._token = token

    def headers(self):
        return {"Authorization": "token %s" % self._token}

    def main_request(self, url, method, data=None):
        if data is None:
            data = {}
        try:
            r = requests.request(method, url, data=json.dumps(data), headers=self.headers())
            return r
        except Exception as error:
            raise NameError(str(error))

    def get(self, url, data=None):
        if data is None:
            data = {}
        return self.main_request(url, 'GET', data=data)

    def post(self, url, data=None):
        if data is None:
            data = {}
        return self.main_request(url, 'POST', data=data)

    def put(self, url, data=None):
        if data is None:
            data = {}
        return self.main_request(url, 'PUT', data=data)

    def delete(self, url):
        return self.main_request(url, 'DELETE')

    @staticmethod
    def get_url(paths):
        url = os.getenv('URL', '')
        for path in paths:
            url = re.sub(r'/?$', re.sub(r'^/?', '/', str(path)), url)
        return url


__main_api__ = None


def main_api():
    global __main_api__
    if __main_api__ is None:
        __main_api__ = ClientRest(token=os.getenv('TOKEN', ''))
    return __main_api__
