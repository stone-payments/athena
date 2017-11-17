import sys
from datetime import datetime
# from pyArango.theExceptions import (UpdateError, CreationError)
from config import *
from graphqlclient import ClientRest
from graphqlclient import GraphQLClient
# from classes import *
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


def find(key, json) -> object:
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

def handling_except(exception):
    if type(exception) == CreationError or type(exception) == UpdateError or type(exception) == KeyError:
        pass
    else:
        print(exception)
        sys.exit(1)


def limit_validation(rate_limit=None, output=None, readme_limit=None):
    if readme_limit is not None:
        with open("queries/rate_limit_query.aql", "r") as query:
            query = query.read()
        prox = pagination_universal(query)
        return limit_validation(rate_limit=find('rateLimit', prox))
    if rate_limit is not None and rate_limit["remaining"] < rate_limit_to_sleep:
        limit_time = (datetime.datetime.strptime(rate_limit["resetAt"], '%Y-%m-%dT%H:%M:%SZ') -
                      datetime.datetime.utcnow()).total_seconds()
        print("wait " + str(limit_time / 60) + " mins")
        if output is not None:
            return time.sleep(limit_time), output.put(rate_limit)
        elif output is None:
            return time.sleep(limit_time)


def parse_multiple_languages(object_to_be_parsed, edge, key, value):
    dictionary = {}
    try:
        for node in find(edge, object_to_be_parsed):
            dictionary[str((find(key, node)))] = round(((find(value, node) /
                                                         find('totalSize', object_to_be_parsed)) * 100), 2)
        return dictionary
    except Exception:
        return None
