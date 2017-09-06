from queue import Queue
from threading import Thread

from pyArango.connection import *

from graphTest import paginationNext
from graphqlclient import GraphQLClient


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
aql = "FOR Repo in Repo return Repo.repoName"
queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True)
# commitCollection = db.createCollection("Commit")
# DevCommitCollection = db.createCollection("DevCommit")
# RepoCommitCollection = db.createCollection("RepoCommit")
# RepoDevCollection = db.createCollection("RepoDev")

commitCollection = db["Commit"]
DevCommitCollection = db["DevCommit"]
RepoCommitCollection = db["RepoCommit"]
RepoDevCollection = db["RepoDev"]

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


def collector(repositories: Queue, output: Queue):
    while True:
        repository = repositories.get(timeout=5)
        print(repository)
        first = True
        cursor = None
        query = '''
query($number_of_repos:Int!, $next:String, $next2:String!){
  repository(owner: "stone-payments", name: $next2) {
    repositoryId: id
    repoName: name
    defaultBranchRef {
      branchName: name
      target {
        ... on Commit {
          history(first: $number_of_repos, after: $next, since: "2017-08-01T00:00:00Z") {
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
                prox = paginationNext(query, cursor, repository)
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
                        "commitId": node["commitId"].replace("/", "@")
                    }
                    output.put(commit)
            except Exception:
                cursor = None
                first = False


repositories_queue = Queue(1500000)
commits_queue = Queue(1500000)

workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(5)]
[t.start() for t in workers]
for repository in queryResult:
    repositories_queue.put(repository)

while True:
    c = commits_queue.get(timeout=5)
    try:
        doc = commitCollection.createDocument()
        doc["repositoryId"] = c["repositoryId"]
        doc["repoName"] = c["repoName"]
        doc["branchName"] = c["branchName"]
        doc["messageHeadline"] = c["messageHeadline"]
        doc["oid"] = c["oid"]
        doc["committedDate"] = c["committedDate"]
        doc["author"] = c["author"]
        doc["devId"] = c["devId"]
        doc["GitHubId"] = c["commitId"]
        doc._key = c["commitId"].replace("/", "@")
        doc.save()
    except Exception:
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
