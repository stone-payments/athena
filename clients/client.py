import json
import time
import requests
from requests.exceptions import ReadTimeout
from custom_configurations.config import max_interval, max_retries
from collection_modules.log_message import log


class Retry:
    def __init__(self, request, interval, times):
        self.request = request
        self.interval = interval
        self.times = times

    def __call__(self, *args, **kwargs):
        for attempts in range(self.times):
            try:
                response = self.request(*args, **kwargs)
                if response.json().get('errors'):
                    raise Exception(response.json())
                return response
            except ReadTimeout as exception_message:
                if attempts == self.times - 1:
                    raise exception_message
            except ConnectionError as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                log.info(message)
                log.info("Github Graphql API is possible down")
                log.info("Resting for 10 min")
                time.sleep(600)
            except Exception as exception_message:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(exception_message).__name__, exception_message.args)
                log.info(message)
                if attempts == self.times - 1:
                    raise exception_message
            time.sleep(self.interval)


def retry(obj, interval, retries):
    for method in [m for m in dir(obj) if not m.startswith('__')]:
        setattr(obj, method, Retry(getattr(obj, method), interval, retries))
    return obj


requests_retry = retry(obj=requests, interval=max_interval, retries=max_retries)


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
            req = requests_retry.post(self.endpoint, json.dumps(data), headers=headers, timeout=self.timeout)
            return req.json()
        else:
            raise NameError("Token is not Defined")


class ClientRest:
    def __init__(self, token, timeout=100.001):
        self.token = token
        self.timeout = timeout

    def execute(self, url: str, query: str, temp: str) -> object:
        query = '{}{}{}'.format(url, query, temp)
        if self.token != "":
            headers = {'Authorization': 'token %s' % self.token}
            req = requests_retry.get(query, headers=headers, timeout=self.timeout)
            if req.json().get("message"):
                time.sleep(5)
            return req.json()
        else:
            raise NameError("Token is not Defined")
