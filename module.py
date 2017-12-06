import datetime
from config import *
from clients import ClientRest
from clients import GraphQLClient
import time

client = GraphQLClient(url, token, timeout)
clientRest2 = ClientRest(token, timeout)


# PAGINATION ###############################


def pagination_universal(query, number_of_repo=None, next_cursor=None, next_repo=None, org=None, slug=None, since=None,
                         until=None):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repo,
                             "next": next_cursor,
                             "next2": next_repo,
                             "org": org,
                             "slug": slug,
                             "sinceTime": since,
                             "untilTime": until
                         })
    return pag


# FIND ###############################


def find(key, json) -> iter:
    if isinstance(json, list):
        for item in json:
            f = find(key, item)
            if f is not None:
                return f
    elif isinstance(json, dict):
        if key in json:
            return json[key]
        else:
            for inner in json.values():
                f = find(key, inner)
                if f is not None:
                    return f
    return None


# HANDLING EXCEPTIONS ###############


def limit_validation(rate_limit=None):
    if rate_limit is not None and rate_limit["remaining"] < rate_limit_to_sleep:
        limit_time = (datetime.datetime.strptime(rate_limit["resetAt"], '%Y-%m-%dT%H:%M:%SZ') -
                      datetime.datetime.utcnow()).total_seconds()
        print("wait " + str(limit_time / 60) + " mins")
        return time.sleep(limit_time)


def parse_multiple_languages(object_to_be_parsed, edge, key, value):
    list_languages = []
    try:
        for node in find(edge, object_to_be_parsed):
            language = {'language': str((find(key, node))), 'size': round(((find(value, node) /
                                                                            find('totalSize',
                                                                                 object_to_be_parsed)) * 100), 2)}
            list_languages.append(language)
        return list_languages
    except Exception as a:
        print(a)
        return None


def convert_datetime(value):
    if value is not None:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return value


def since_time(since_time_delta):
    return (datetime.datetime.utcnow() + datetime.timedelta(since_time_delta)).strftime('%Y-%m-%d') + "T00:00:00Z"


def until_time(until_time_delta):
    return (datetime.datetime.utcnow() + datetime.timedelta(until_time_delta)).strftime('%Y-%m-%d') + "T00:00:00Z"
