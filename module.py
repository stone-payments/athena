import sys

from pyArango.theExceptions import (UpdateError, CreationError)

from config import *
from graphqlclient import ClientRest
from graphqlclient import GraphQLClient

client = GraphQLClient(url, token, timeout)
clientRest2 = ClientRest(token, timeout)


# PAGINATION ###############################


def pagination_universal(query, number_of_repo=None, next=None, next2=None, org=None, slug=None, since=None,
                         until=None):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repo,
                             "next": next,
                             "next2": next2,
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

def handling_except(exception_type):
    if exception_type == CreationError or exception_type == UpdateError or exception_type == KeyError:
        pass
    else:
        print(exception_type)
        sys.exit(1)
