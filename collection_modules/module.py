import datetime
import time

from clients import ClientRest
from clients import GraphQLClient
from collection_modules.log_message import *
from custom_configurations.config import url, token, token_webhook, timeout, rate_limit_to_sleep

client_graphql = GraphQLClient(url, token, timeout)
client_graphql_webhook = GraphQLClient(url, token_webhook, timeout)
client_rest = ClientRest(token, timeout)


def find_key(key, json) -> iter:
    if isinstance(json, list):
        for item in json:
            f = find_key(key, item)
            if f is not None: return f
    elif isinstance(json, dict):
        if key in json: return json[key]
        for inner in json.values():
            f = find_key(key, inner)
            if f is not None: return f
    return None


def limit_validation(rate_limit=None):
    if rate_limit is not None and rate_limit["remaining"] < rate_limit_to_sleep:
        limit_time = (datetime.datetime.strptime(rate_limit["resetAt"], '%Y-%m-%dT%H:%M:%SZ') -
                      datetime.datetime.utcnow()).total_seconds()
        log.info('{} {} {}'.format('wait', str(limit_time / 60), 'mins'))
        return time.sleep(limit_time)


def parse_multiple_languages(object_to_be_parsed, edge, key, value):
    if find_key(edge, object_to_be_parsed) is not None:
        return [{'language': str((find_key(key, node))), 'size': round(((find_key(value, node) /
                                                                         find_key('totalSize',
                                                                                  object_to_be_parsed)) * 100), 2)} for
                node in find_key(edge, object_to_be_parsed)]
    return None


def convert_datetime(value):
    if value is not None:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return value


def utc_time(since_time_delta):
    return '{}{}'.format((datetime.datetime.utcnow() + datetime.timedelta(int(since_time_delta))).strftime('%Y-%m-%d'),
                         "T00:00:00Z")


def utc_time_datetime_format(since_time_delta):
    return datetime.datetime.utcnow() + datetime.timedelta(hours=int(since_time_delta))
