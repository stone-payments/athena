from queue import Queue
from threading import Thread

from pyArango.connection import *

from graphTest import paginatioOrgDate
from graphqlclient import ClientRest
from graphqlclient import GraphQLClient

######conection info##########################################################
token = '117d1985b8c852c7ecbd9980d16568ed023479ed'
##############################################################################

clientRest2 = ClientRest(token)


def restQuery(url, query, temp):
    result = clientRest2.execute(query=url + query + temp)
    return result


def parse_list(other):
    result = []
    for x in other:
        if isinstance(x, dict):
            result.append(Mapper(x))
        elif isinstance(x, list):
            result.append(parse_list(x))
        else:
            result.append(x)
    return result


class Mapper(dict):
    """
    A fancy dict that give the user seamless use between keys and attributes
    """

    def __init__(self, other):
        super(dict, self).__init__()
        for key, value in other.items():
            key = key.lower().replace('_', '')
            if isinstance(value, dict):
                self[key] = Mapper(value)
            elif isinstance(value, list):
                self[key] = parse_list(value)
            else:
                self[key] = value

    def __setattr__(self, key, value):
        key = key.lower().replace('_', '')
        self[key] = value

    def __getattr__(self, item):
        item = item.lower().replace('_', '')
        return self[item]


conn = Connection(username="root", password="")
db = conn["athena3"]

# commitCollection = db.createCollection("Commit")
# DevCommitCollection = db.createCollection("DevCommit")
# RepoCommitCollection = db.createCollection("RepoCommit")
# RepoDevCollection = db.createCollection("RepoDev")
# forkCollection = db.createCollection("Fork")
# devFork = db.createCollection("DevFork")
# repoFork = db.createCollection("RepoFork")
# db['Commit'].ensureHashIndex(['devId'],unique=False, sparse=False)
# db['Commit'].ensureHashIndex(['author'],unique=False, sparse=False)
# db['Commit'].ensureSkiplistIndex(['committedDate'],unique=False, sparse=False)
db['Commit'].ensureHashIndex(['org'], unique=False, sparse=False)

commitCollection = db["Commit"]
DevCommitCollection = db["DevCommit"]
RepoCommitCollection = db["RepoCommit"]
RepoDevCollection = db["RepoDev"]
ForkCollection = db["Fork"]
DevForkCollection = db["DevFork"]
RepoForkCollection = db["RepoFork"]

def new_client():
    ######conection info##########################################################
    token = '117d1985b8c852c7ecbd9980d16568ed023479ed'
    url = 'https://api.github.com/graphql'
    ##############################################################################
    number_of_repos = 50
    return GraphQLClient(url, token)


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


urlCommit = 'https://api.github.com/repos/'


def commitcollector(org):
    aql = "FOR Repo in Repo FILTER Repo.org == @org return Repo.repoName"
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            print(repository)
            first = True
            cursor = None
            query = '''
    query($number_of_repos:Int!, $next:String, $next2:String!,$org:String!){
      repository(owner: $org, name: $next2) {
        repositoryId: id
        repoName: name
        defaultBranchRef {
          branchName: name
          target {
            ... on Commit {
              history(first: $number_of_repos, after: $next, since: "2017-09-01T00:00:00Z") {
                pageInfo {
                  endCursor
                }
                edges {
                  node {
                    commitId: id
                    messageHeadline
                    oid
                    committedDate
                    author {
                      user {
                        devId: id
                        login
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    '''
            while cursor is not None or first:
                first = False
                try:
                    prox = paginatioOrgDate(query, cursor, repository, org)
                    if prox.get("documentation_url"):
                        print("ERROR")
                    cursor = find('endCursor', prox)
                    prox_node = find('repository', prox)
                    commits = find('edges', prox_node)
                    repository_id = prox_node["repositoryId"]
                    repo_name = prox_node["repoName"]
                    branch_name = prox_node["defaultBranchRef"]["branchName"]
                    for c in commits:
                        node = c["node"]
                        author = node["author"]
                        user = author["user"] or {'login': 'anonimo', 'devId': 'anonimo'}
                        commit = {
                            "repositoryId": repository_id,
                            "repoName": repo_name,
                            "branchName": branch_name,
                            "messageHeadline": node["messageHeadline"],
                            "oid": node["oid"],
                            "committedDate": node["committedDate"],
                            "author": user.get("login"),
                            "devId": user.get("devId"),
                            "GitHubId": node["commitId"],
                            "commitId": node["commitId"].replace("/", "@"),
                            "org": org
                        }
                        output.put(commit)
                except Exception:
                    cursor = None
                    first = False

    def save(repositories: Queue, output: Queue):
        while True:
            c = commits_queue.get(timeout=150)
            try:
                try:
                    doc = commitCollection[str(c["commitId"].replace("/", "@"))]
                except Exception:
                    doc = commitCollection.createDocument()
                    pass
                doc["repositoryId"] = c["repositoryId"]
                doc["repoName"] = c["repoName"]
                doc["branchName"] = c["branchName"]
                doc["messageHeadline"] = c["messageHeadline"]
                doc["oid"] = c["oid"]
                doc["committedDate"] = c["committedDate"]
                doc["author"] = c["author"]
                doc["devId"] = c["devId"]
                doc["GitHubId"] = c["commitId"]
                doc["org"] = c["org"]
                doc._key = c["commitId"].replace("/", "@")
                doc.save()
            except Exception as a:
                print(a)
                pass
            try:
                temp = db['Commit'][str(c["commitId"])]
                temp2 = db['Dev'][str(c["devId"])]
                commitDoc = DevCommitCollection.createEdge()
                commitDoc["_key"] = (str(c["commitId"]) + str(c["devId"])).replace("/", "@")
                commitDoc.links(temp2, temp)
                commitDoc.save()
            except Exception:
                pass
            try:
                temp = db['Commit'][str(c["commitId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                RepoDoc = RepoCommitCollection.createEdge()
                RepoDoc["_key"] = (str(c["commitId"]) + str(c["repositoryId"])).replace("/", "@")
                RepoDoc.links(temp2, temp)
                RepoDoc.save()
            except Exception:
                pass
            try:
                temp = db['Dev'][str(c["devId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                DevDoc = RepoDevCollection.createEdge()
                DevDoc["_key"] = (str(c["repositoryId"]) + str(c["devId"])).replace("/", "@")
                DevDoc.links(temp2, temp)
                DevDoc.save()
            except Exception:
                pass

    repositories_queue = Queue(1500000)
    commits_queue = Queue(1500000)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(5)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(5)]
    for repository in queryResult:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


def statscollector(org):
    aql = """FOR Commit IN Commit
    FILTER Commit.additions == null
    FILTER Commit.org == @org
    FILTER Commit.committedDate > "2017-08-01T00:00:00Z"
    RETURN {oid:Commit.oid,repo:Commit.repoName,id:Commit.GitHubId}"""
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            print(repository["oid"])
            try:
                temp = repository["oid"]
                query = org + "/" + repository["repo"] + '/commits/'
                result = restQuery(urlCommit, query, temp)
            except Exception as a:
                print(a)
                continue
            commit = {
                "commitId": repository["id"],
                'totalAddDel': result['stats']['total'],
                'additions': result['stats']['additions'],
                'deletions': result['stats']['deletions'],
                'numFiles': len(result['files'])
            }
            output.put(commit)
            # repositories.task_done()

    def save(repositories: Queue, output: Queue):
        while True:
            c = commits_queue.get(timeout=10)
            print("entrou")
            try:
                doc = commitCollection[str(c["commitId"].replace("/", "@"))]
                doc['totalAddDel'] = c['totalAddDel']
                doc['additions'] = c['additions']
                doc['deletions'] = c['deletions']
                doc['numFiles'] = c['numFiles']
                doc._key = c["commitId"].replace("/", "@")
                doc.save()
            except Exception as a:
                print(a)
                pass

    repositories_queue = Queue(1500000)
    commits_queue = Queue(1500000)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(5)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(5)]

    for repository in queryResult:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


def forkCollector(org):
    aql = "FOR Repo in Repo FILTER Repo.org == @org return Repo.repoName"
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            print(repository)
            first = True
            cursor = None
            query = '''
    query($number_of_repos:Int!, $next:String, $next2:String!,$org:String!){
      organization(login: $org) {
        repository(name: $next2) {
          repositoryId:id
          repoName:name
          forks(first: $number_of_repos , after:$next) {
          pageInfo{
              endCursor
            }
            edges {
              node {
                createdAt
                forkId: id
                isPrivate
                isLocked
                lockReason
                owner {
                 devId: id
                  login
                }
              }
            }
          }
        }
      }
    }
    '''
            while cursor is not None or first:
                first = False
                try:
                    prox = paginatioOrgDate(query, cursor, repository, org)
                    if prox.get("documentation_url"):
                        print("ERROR")
                    cursor = find('endCursor', prox)
                    prox_node = find('repository', prox)
                    forks = find('edges', prox_node)
                    repository_id = prox_node["repositoryId"]
                    repo_name = prox_node["repoName"]

                    for c in forks:
                        print("AE")
                        node = c["node"]
                        print(node)
                        author = node["owner"] or {'devId': 'anonimo', 'login': 'anonimo'}
                        print(author)
                        commit = {
                            "repositoryId": repository_id,
                            "repoName": repo_name,
                            "createdAt": node["createdAt"],
                            "id": node["forkId"],
                            "isPrivate": node["isPrivate"],
                            "isLocked": node["isLocked"],
                            "devId": author.get("devId"),
                            "login": author.get("login"),
                            "forkId": node["forkId"],
                            "org": org
                        }
                        print("foi")
                        output.put(commit)
                except Exception as a:
                    print(a)
                    cursor = None
                    first = False

    def save(repositories: Queue, output: Queue):
        while True:
            c = commits_queue.get(timeout=150)
            print(c)
            try:
                try:
                    doc = ForkCollection[str(c["forkId"].replace("/", "@"))]
                except Exception:
                    doc = ForkCollection.createDocument()
                    pass
                doc["repositoryId"] = c["repositoryId"]
                doc["repoName"] = c["repoName"]
                doc["createdAt"] = c["createdAt"]
                doc["id"] = c["id"]
                doc["isPrivate"] = c["isPrivate"]
                doc["isLocked"] = c["isLocked"]
                doc["devId"] = c["devId"]
                doc["login"] = c["login"]
                doc["forkId"] = c["forkId"]
                doc["org"] = c["org"]
                doc._key = c["forkId"].replace("/", "@")
                doc.save()
            except Exception as a:
                print(a)
                pass
            try:
                temp = db['Fork'][str(c["forkId"])]
                temp2 = db['Dev'][str(c["devId"])]
                commitDoc = DevForkCollection.createEdge()
                commitDoc["_key"] = (str(c["forkId"]) + str(c["devId"])).replace("/", "@")
                commitDoc.links(temp2, temp)
                commitDoc.save()
            except Exception:
                pass
            try:
                temp = db['Fork'][str(c["forkId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                RepoDoc = RepoForkCollection.createEdge()
                RepoDoc["_key"] = (str(c["forkId"]) + str(c["repositoryId"])).replace("/", "@")
                RepoDoc.links(temp2, temp)
                RepoDoc.save()
            except Exception:
                pass

    repositories_queue = Queue(1500000)
    commits_queue = Queue(1500000)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(5)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(5)]
    for repository in queryResult:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# commitcollector("pagarme")
# statscollector("pagarme")
forkCollector("stone-payments")
