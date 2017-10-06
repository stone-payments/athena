from pyArango.connection import *

from config import *
from graphqlclient import ClientRest
from graphqlclient import GraphQLClient

client = GraphQLClient(url, token, timeout)
clientRest2 = ClientRest(token, timeout)


######### Create DataBase ################################################

def start_db():
    conn = Connection(arangoURL=db_url, username=username, password=password)
    try:
        db = conn.createDatabase(name=db_name)
        return db
    except Exception:
        db = conn[db_name]
        return db


######### Create Collections ##############################################


def createcollections(db):
    try:
        db["Repo"]
    except Exception:
        db.createCollection("Repo")
    try:
        db['Dev']
    except Exception:
        db.createCollection('Dev')
    try:
        db["Teams"]
    except Exception:
        db.createCollection("Teams")
    try:
        db["Languages"]
    except Exception:
        db.createCollection("Languages")
    try:
        db["LanguagesRepo"]
    except:
        db.createCollection("LanguagesRepo")
    try:
        db["Commit"]
    except Exception:
        db.createCollection("Commit")
    try:
        db["DevCommit"]
    except:
        db.createCollection("DevCommit")
    try:
        db["RepoCommit"]
    except:
        db.createCollection("RepoCommit")
    try:
        db["RepoDev"]
    except:
        db.createCollection("RepoDev")
    try:
        db["Commit"]
    except Exception:
        db.createCollection["Commit"]
    try:
        db["Fork"]
    except Exception:
        db.createCollection("Fork")
    try:
        db["DevFork"]
    except Exception:
        db.createCollection("DevFork")
    try:
        db["RepoFork"]
    except Exception:
        db.createCollection("RepoFork")
    try:
        db["Issue"]
    except Exception:
        db.createCollection("Issue")
    try:
        db["RepoIssue"]
    except:
        db.createCollection("RepoIssue")
    try:
        db["TeamsDev"]
    except Exception:
        db.createCollection("TeamsDev")
    try:
        db["TeamsRepo"]
    except Exception:
        db.createCollection("TeamsRepo")
    db['Dev'].ensureHashIndex(['devName'], unique=False, sparse=False)
    db['Dev'].ensureHashIndex(['login'], unique=False, sparse=False)
    db['Teams'].ensureHashIndex(['teamName'], unique=False, sparse=False)
    db['Languages'].ensureHashIndex(['name'], unique=True, sparse=False)
    db['Commit'].ensureHashIndex(['org'], unique=False, sparse=False)
    db['Issue'].ensureHashIndex(['repoName'], unique=False, sparse=False)
    db['Issue'].ensureSkiplistIndex(['closedAt'], unique=False, sparse=False)
    db['Issue'].ensureSkiplistIndex(['createdAt'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['readme'], unique=False, sparse=False)


######pagination############################################################


def paginationuniversal(query, number_of_repo=None, next=None, next2=None, org=None, slug=None, sinceTime=None,
                        untilTime=None):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repo,
                             "next": next,
                             "next2": next2,
                             "org": org,
                             "slug": slug,
                             "sinceTime": sinceTime,
                             "untilTime": untilTime
                         })
    return pag


####### Find ######################################################################


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
