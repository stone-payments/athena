from queue import Queue
from threading import Thread

import pyArango
import pyArango.validation as VAL
from pyArango.collection import Collection, Field

from config import *
from graphqlclient import ClientRest
from graphqlclient import GraphQLClient

client = GraphQLClient(url, token, timeout)
clientRest2 = ClientRest(token, timeout)


def restQuery(url, query, temp):
    result = clientRest2.execute(url, query, temp)
    return result
######## Classes #########################################################

class TeamsDev(pyArango.collection.Edges):
    _fields = dict(
    )

class TeamsRepo(pyArango.collection.Edges):
    _fields = dict(
    )

class DevCommit(pyArango.collection.Edges):
    _fields = dict(
    )

class RepoCommit(pyArango.collection.Edges):
    _fields = dict(
    )

class RepoFork(pyArango.collection.Edges):
    _fields = dict(
    )

class DevFork(pyArango.collection.Edges):
    _fields = dict(
    )

class RepoIssue(pyArango.collection.Edges):
    _fields = dict(
    )

class LanguagesRepo(pyArango.collection.Edges):
    _fields = dict(
        size=Field(validators=[VAL.NotNull()]),
    )

class RepoDev(pyArango.collection.Edges):
    _fields = dict(
    )

class Languages(Collection):
    """
    LANGUAGES
    """
    _validation = {
        'allow_foreign_fields': False  # allow fields that are not part of the schema
    }
    _fields = dict(
        name=Field(validators=[VAL.NotNull()]),
        id=Field(validators=[VAL.NotNull()])
    )

class Teams(Collection):
    """
    TEAMS
    """
    _validation = {
        'allow_foreign_fields': False  # allow fields that are not part of the schema
    }
    _fields = dict(
        createdAt=Field(validators=[VAL.NotNull()]),
        teamName=Field(validators=[VAL.NotNull()]),
        privacy=Field(validators=[VAL.NotNull()]),
        slug=Field(validators=[VAL.NotNull()]),
        childTeams=Field(),
        childTeamsTotal=Field(),
        ancestors=Field(),
        id=Field(validators=[VAL.NotNull()]),
        org=Field(validators=[VAL.NotNull()])
    )


class Commit(Collection):
    """
    COMMIT
    """
    _validation = {
        'allow_foreign_fields': False  # allow fields that are not part of the schema
    }
    _fields = dict(
        messageHeadline=Field(),
        oid=Field(validators=[VAL.NotNull()]),
        committedDate=Field(validators=[VAL.NotNull()]),
        author=Field(),
        devId=Field(validators=[VAL.NotNull()]),
        GitHubId=Field(validators=[VAL.NotNull()]),
        repositoryId=Field(validators=[VAL.NotNull()]),
        repoName=Field(validators=[VAL.NotNull()]),
        branchName=Field(),
        commitId=Field(validators=[VAL.NotNull()]),
        org=Field(validators=[VAL.NotNull()]),
        totalAddDel=Field(validators=[VAL.NotNull()]),
        additions=Field(validators=[VAL.NotNull()]),
        deletions=Field(validators=[VAL.NotNull()]),
        numFiles=Field(validators=[VAL.NotNull()]),
    )

class Dev(Collection):
    """
    DEV
    """
    _validation = {
        'allow_foreign_fields': False  # allow fields that are not part of the schema
    }
    _fields = dict(
        devName=Field(),
        followers=Field(),
        following=Field(),
        login=Field(validators=[VAL.NotNull()]),
        avatarUrl=Field(),
        contributedRepositories=Field(),
        pullRequests=Field(),
        id=Field(validators=[VAL.NotNull()]),
        org=Field(validators=[VAL.NotNull()]),
    )


class Repo(Collection):
    """
    REPO
    """
    _validation = {
        'allow_foreign_fields': False  # allow fields that are not part of the schema
    }
    _fields = dict(
        repoName=Field(),
        description=Field(),
        url=Field(),
        openSource=Field(validators=[VAL.NotNull()]),
        primaryLanguage=Field(),
        forks=Field(),
        stargazers=Field(),
        watchers=Field(),
        createdAt=Field(),
        nameWithOwner=Field(),
        licenseId=Field(),
        licenseType=Field(),
        id=Field(validators=[VAL.NotNull()]),
        org=Field(validators=[VAL.NotNull()])
    )

class Fork(Collection):
    """
    Fork
    """
    _fields = dict(
        repositoryId=Field(validators=[VAL.NotNull()]),
        repoName=Field(),
        createdAt=Field(validators=[VAL.NotNull()]),
        id=Field(validators=[VAL.NotNull()]),
        isPrivate=Field(validators=[VAL.NotNull()]),
        isLocked=Field(),
        devId=Field(validators=[VAL.NotNull()]),
        login=Field(),
        forkId=Field(validators=[VAL.NotNull()]),
        org=Field(validators=[VAL.NotNull()])
    )

class Issue(Collection):
    """
    Issue
    """
    _fields = dict(
        repositoryId=Field(validators=[VAL.NotNull()]),
        repoName=Field(),
        state=Field(),
        closedAt=Field(),
        author=Field(),
        issueId=Field(validators=[VAL.NotNull()]),
        createdAt=Field(validators=[VAL.NotNull()]),
        closed=Field(),
        label=Field(),
        title=Field(),
        org=Field(validators=[VAL.NotNull()])
    )


######pagination############################################################


def pagination(query, number_of_repo, tmp, org):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repo,
                             "next": tmp,
                             "org": org
                         })
    return pag


def paginationRepoNum(query, tmp, num):
    pag = client.execute(query,
                         {
                             "number_of_repos": num,
                             "next": tmp
                         })
    return pag


def paginationOrg(query, tmp, num):
    pag = client.execute(query,
                         {
                             "org": tmp,
                             "next": num
                         })
    return pag


def paginationSlug(query, tmp, slugTemp, org):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repos,
                             "next": tmp,
                             "slug": slugTemp,
                             "org": org
                         })
    return pag


def paginationNext(query, next, next2, org):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repos,
                             "next": next,
                             "next2": next2,
                             "org": org
                         })
    return pag


def paginatioOrgDate(query, next, next2, org, sinceTime, untilTime):
    pag = client.execute(query,
                         {
                             "number_of_repos": number_of_repos,
                             "next": next,
                             "next2": next2,
                             "org": org,
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

### Connection #####################################################################

# conn = Connection(username="root", password="")
# try:
#     db = conn.createDatabase(name="athena3")
# except Exception:
#     db = conn["athena3"]

# ##### Repo #######################################################################
def RepoQuery(org):
    with open("repoQuery.txt", "r") as query:
        query = query.read()
    try:
        repoCollection = db.createCollection("Repo")
    except Exception:
        repoCollection = db["Repo"]
    db['Repo'].ensureHashIndex(['repoName'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['isPrivate'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['licenseId'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['licenseType'], unique=False, sparse=False)

    count = 0
    first = True
    cursor = None
    while cursor or first:
        try:
            prox = pagination(query, number_of_repos, cursor, org)
            proxRepositorios = prox["data"]["organization"]["repositories"]["edges"]
            for repo in proxRepositorios:
                try:
                    count = count + 1
                    try:
                        doc = repoCollection[str(repo["node"]["id"].replace("/", "@"))]
                    except:
                        doc = repoCollection.createDocument()
                        pass
                    doc['repoName'] = repo["node"]["name"]
                    doc["description"] = repo["node"]["description"]
                    doc["url"] = repo["node"]["url"]
                    doc["openSource"] = False if repo["node"]["isPrivate"] else True
                    doc["primaryLanguage"] = find('priLanguage', repo)
                    doc["forks"] = repo["node"]["forks"]["totalCount"]
                    doc["stargazers"] = repo["node"]["stargazers"]["totalCount"]
                    doc["watchers"] = repo["node"]["watchers"]["totalCount"]
                    doc["createdAt"] = repo["node"]["createdAt"]
                    doc["nameWithOwner"] = repo["node"]["nameWithOwner"]
                    doc["licenseId"] = find('licenseId', repo)
                    print(repo["node"]["name"])
                    doc["licenseType"] = find('licenseType', repo)
                    doc["id"] = repo["node"]["id"].replace("/", "@")
                    doc["org"] = org
                    doc._key = repo["node"]["id"].replace("/", "@")
                    doc.save()
                except Exception as a:
                    print(a)
                    pass
            cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
        except Exception as a:
            print(a)
            cursor = False
            first = False
    print(count)

###### Dev #########################################################################################################
def dev(org):
    try:
        devCollection = db.createCollection('Dev')
    except Exception:
        devCollection = db['Dev']
    db['Dev'].ensureHashIndex(['devName'], unique=False, sparse=False)
    db['Dev'].ensureHashIndex(['login'], unique=False, sparse=False)

    with open("devQuery.txt", "r") as query:
        query = query.read()
    count = 0
    first = True
    cursor = None
    while cursor or first:
        try:
            prox = pagination(query, 30, cursor, org)
            print(prox)
            proxRepositorios = prox["data"]["organization"]["members"]["edges"]
            for i in proxRepositorios:
                count = count + 1
                try:
                    doc = devCollection[str(i["node"]["id"].replace("/", "@"))]
                except Exception:
                    doc = devCollection.createDocument()
                doc['devName'] = i["node"]["name"]
                doc["followers"] = i["node"]["followers"]["totalCount"]
                doc["following"] = i["node"]["following"]["totalCount"]
                doc["login"] = i["node"]["login"]
                doc["avatarUrl"] = i["node"]["avatarUrl"]
                doc["contributedRepositories"] = i["node"]["contributedRepositories"]["totalCount"]
                doc["pullRequests"] = i["node"]["pullRequests"]["totalCount"]
                doc["id"] = i["node"]["id"].replace("/", "@")
                doc["org"] = org
                doc._key = i["node"]["id"].replace("/", "@")
                doc.save()
                print(count)
            cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
        except Exception:
            cursor = False
            first = False

###### Teams #########################################################################################
def Teams(org):
    try:
        TeamsCollection = db.createCollection("Teams")
    except Exception:
        TeamsCollection = db["Teams"]
    db['Teams'].ensureHashIndex(['teamName'], unique=False, sparse=False)

    with open("teamsQuery.txt", "r") as query:
        query = query.read()

    count = 0
    first = True
    cursor = None
    while cursor is not None or first:
        first = False
        try:
            prox = pagination(query, 50, cursor, org)
            cursor = find('endCursor', prox)
            proxRepositorios = prox["data"]["organization"]["teams"]["edges"]
            for i in proxRepositorios:
                count = count + 1
                try:
                    doc = TeamsCollection[str(i["node"]["id"].replace("/", "@"))]
                except Exception:
                    doc = TeamsCollection.createDocument()
                doc['createdAt'] = i["node"]["createdAt"]
                doc["teamName"] = i["node"]["name"]
                print(i["node"]["name"])
                doc["privacy"] = i["node"]["privacy"]
                doc["slug"] = i["node"]["slug"]
                doc["childTeams"] = i["node"]["childTeams"]["nodes"]
                doc["childTeamsTotal"] = i["node"]["childTeams"]["totalCount"]
                doc["ancestors"] = i["node"]["ancestors"]["nodes"]
                doc["id"] = i["node"]["id"].replace("/", "@")
                doc["org"] = org
                doc._key = i["node"]["id"].replace("/", "@")
                doc.save()
                print(count)
        except Exception:
            cursor = None
            first = False





###### TeamsDev #########################################################################################################
def teamsDev(org):
    try:
        TeamsDevCollection = db.createCollection("TeamsDev")
    except Exception:
        TeamsDevCollection = db["TeamsDev"]
    bindVars = {"org": org}
    aql = "FOR Teams in Teams FILTER Teams.org == @org return Teams.slug"
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, bindVars=bindVars)

    with open("teamsDevQuery.txt", "r") as query:
        query = query.read()

    count = 0
    for x in queryResult:
        first = True
        cursor = None
        while cursor or first:
            try:
                prox = paginationSlug(query, cursor, x, org)
                proxNode = prox["data"]["organization"]["team"]
                i = proxNode["members"]["edges"]
                for j in i:
                    count = count + 1
                    try:
                        temp = db['Dev'][str(j["node"]["id"]).replace("/", "@")]
                        print(temp)
                        temp2 = db['Teams'][str(proxNode["id"]).replace("/", "@")]
                        print(temp2)
                        doc = TeamsDevCollection.createEdge()
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception:
                        pass
                cursor = prox["data"]["organization"]["team"]["members"]["pageInfo"]["endCursor"]
                if cursor is None:
                    cursor = False
            except Exception as a:
                print(a)
                cursor = False
                first = False
    print(count)


# #### teamsRepo #######################################################################

def teamsRepo(org):
    try:
        TeamsRepoCollection = db.createCollection("TeamsRepo")
    except Exception:
        TeamsRepoCollection = db["TeamsRepo"]
    bindVars = {"org": org}
    aql = "FOR Teams in Teams FILTER Teams.org == @org return Teams.slug"
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, bindVars=bindVars)

    with open("teamsRepoQuery.txt", "r") as query:
        query = query.read()

    count = 0
    for x in queryResult:
        first = True
        cursor = None
        while cursor or first:
            try:
                prox = paginationSlug(query, cursor, x, org)
                proxNode = prox["data"]["organization"]["team"]
                i = proxNode["repositories"]["edges"]
                for j in i:
                    count = count + 1
                    try:
                        temp = db['Repo'][str(j["node"]["id"]).replace("/", "@")]
                        print(temp)
                        temp2 = db['Teams'][str(proxNode["id"]).replace("/", "@")]
                        print(temp2)
                        doc = TeamsRepoCollection.createEdge()
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception:
                        pass
                cursor = prox["data"]["organization"]["team"]["repositories"]["pageInfo"]["endCursor"]
                if cursor is None:
                    cursor = False
            except Exception as a:
                print(a)
                cursor = False
                first = False
    print(count)

##### Languages #########################################################################################################
def languages(org):
    try:
        LanguagesCollection = db.createCollection("Languages")
    except Exception:
        LanguagesCollection = db["Languages"]
        pass
    try:
        LanguagesRepoCollection = db.createCollection("LanguagesRepo")
    except:
        LanguagesRepoCollection = db["LanguagesRepo"]
        pass
    db['Languages'].ensureHashIndex(['name'], unique=True, sparse=False)

    aql = "FOR Repo in Repo FILTER Repo.org == @org return Repo.repoName"
    bindVars = {"org": org}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)

    with open("languagesQuery.txt", "r") as query:
        query = query.read()

    for repositoryname in queryResult:
        first = True
        cursor = None
        while cursor or first:
            first = False
            print(repositoryname)
            try:
                prox = paginationNext(query, cursor, repositoryname, org)
                print(prox)
                cursor = find('endCursor', prox)
                proxNode = find('languages', prox)
                edges = find('edges', proxNode)
                for node in edges:
                    try:
                        doc = LanguagesCollection.createDocument()
                        doc["name"] = find('name', node)
                        doc["id"] = find('id', node)
                        doc._key = find('id', node).replace("/", "@")
                        doc.save()
                    except Exception:
                        pass
                    try:
                        temp = db['Languages'][str(node["node"]["id"]).replace("/", "@")]
                        temp2 = db['Repo'][str(find('repositoryId', prox)).replace("/", "@")]
                        doc = LanguagesRepoCollection.createEdge(
                            {"size": round(((node['size'] / find('totalSize', prox)) * 100), 2)})
                        doc._key = (str(node["node"]["id"]) + str(find('repositoryId', prox))).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception:
                        pass
            except Exception as a:
                print(a)
                cursor = False
                first = False


########################################################################################################

def commitcollector(org):
    try:
        commitCollection = db.createCollection("Commit")
    except Exception:
        commitCollection = db["Commit"]
        pass
    try:
        db['Commit'].ensureHashIndex(['org'], unique=False, sparse=False)
    except Exception:
        pass
    try:
        DevCommitCollection = db.createCollection("DevCommit")
    except:
        DevCommitCollection = db["DevCommit"]
        pass
    try:
        RepoCommitCollection = db.createCollection("RepoCommit")
    except:
        RepoCommitCollection = db["RepoCommit"]
        pass
    try:
        RepoDevCollection = db.createCollection("RepoDev")
    except:
        RepoDevCollection = db["RepoDev"]
        pass
    aql = "FOR Repo in Repo FILTER Repo.org == @org return Repo.repoName"
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)
    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            print(repository)
            first = True
            cursor = None
            with open("commitQuery.txt", "r") as query:
                query = query.read()
            while cursor is not None or first:
                first = False
                try:
                    prox = paginatioOrgDate(query, cursor, repository, org, sinceTime, untilTime)
                    print(prox)
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


# #### Readme #######################################################################

def readme(org):
    aql = "FOR Repo in Repo FILTER Repo.org == @org return {repoName:Repo.repoName,key:Repo._key}"
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)
    db['Repo'].ensureHashIndex(['readme'], unique=False, sparse=False)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            print(repository['repoName'])
            with open("readmeQuery.txt", "r") as query:
                query = query.read()
            try:
                prox = paginationOrg(query, org, repository['repoName'])
                output.put(1)
                if prox.get('errors'):
                    doc = db['Repo'][str(repository['key'])]
                    doc["readme"] = None
                    doc.save()
                    continue
                try:
                    a = find('ranges', prox)
                    doc = db["Repo"][str(find('id', prox))]
                    doc["readme"] = "OK" if a[-1]['endingLine'] >= 5 else "Poor"
                    doc.save()
                except Exception:
                    continue
            except Exception as a:
                pass

    count_queue = Queue(15000)
    repositories_queue = Queue(15000)
    workers = [Thread(target=collector, args=(repositories_queue, count_queue)) for _ in range(5)]
    for repository in queryResult:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.join() for t in workers]
    print(count_queue.qsize())


#############################################################################################################

def statscollector(org):
    try:
        commitCollection = db.createCollection["Commit"]
    except Exception:
        commitCollection = db["Commit"]
        pass
    with open("statsQuery.txt", "r") as aql:
        aql = aql.read()
    bindVars = {"org": org, "sinceTime": sinceTime, "untilTime": untilTime}
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
    try:
        ForkCollection = db.createCollection("Fork")
    except Exception:
        ForkCollection = db["Fork"]
        pass
    try:
        DevForkCollection = db.createCollection("DevFork")
    except Exception:
        DevForkCollection = db["DevFork"]
        pass
    try:
        RepoForkCollection = db.createCollection("RepoFork")
    except Exception:
        RepoForkCollection = db["RepoFork"]
        pass
    aql = "FOR Repo in Repo FILTER Repo.org == @org return Repo.repoName"
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            print(repository)
            first = True
            cursor = None
            with open("forkQuery.txt", "r") as query:
                query = query.read()
            while cursor is not None or first:
                first = False
                try:
                    prox = paginationNext(query, cursor, repository, org)
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


def issue(org):
    try:
        IssueCollection = db.createCollection("Issue")
    except Exception:
        IssueCollection = db["Issue"]
        pass
    try:
        db['Issue'].ensureHashIndex(['repoName'], unique=False, sparse=False)
        db['Issue'].ensureSkiplistIndex(['closedAt'], unique=False, sparse=False)
        db['Issue'].ensureSkiplistIndex(['createdAt'], unique=False, sparse=False)
    except Exception:
        pass
    try:
        RepoIssueCollection = db.createCollection("RepoIssue")
    except:
        RepoIssueCollection = db["RepoIssue"]
        pass
    aql = "FOR Repo in Repo FILTER Repo.org == @org return Repo.repoName"
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True, bindVars=bindVars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            print(repository)
            first = True
            cursor = None
            with open("issueQuery.txt", "r") as query:
                query = query.read()
            while cursor is not None or first:
                first = False
                try:
                    prox = paginationNext(query, cursor, repository, org)
                    if prox.get("documentation_url"):
                        print("ERROR")
                    cursor = find('endCursor', prox)
                    prox_node = find('repository', prox)
                    issues = find('edges', prox_node)
                    repository_id = prox_node["repositoryId"]
                    repo_name = prox_node["repoName"]

                    for c in issues:
                        print("AE")
                        node = c["node"]
                        print(node)
                        author = find('author', node)
                        print(author)
                        commit = {
                            "repositoryId": repository_id,
                            "repoName": repo_name,
                            "state": find('state', c),
                            "closedAt": find('closedAt', c),
                            "author": find('author', c),
                            "issueId": find('issueId', c),
                            "createdAt": find('createdAt', c),
                            "closed": find('closed', c),
                            "label": find('label', c),
                            "title": find('title', c),
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
                    doc = IssueCollection[str(c["issueId"].replace("/", "@"))]
                except Exception:
                    doc = IssueCollection.createDocument()
                    pass
                doc["repositoryId"] = c["repositoryId"]
                doc["repoName"] = c["repoName"]
                doc["state"] = c["state"]
                doc["closedAt"] = c["closedAt"]
                doc["author"] = c["author"]
                doc["issueId"] = c["issueId"]
                doc["createdAt"] = c["createdAt"]
                doc["closed"] = c["closed"]
                doc["label"] = c["label"]
                doc["title"] = c["title"]
                doc["org"] = c["org"]
                doc._key = c["issueId"].replace("/", "@")
                doc.save()
            except Exception as a:
                print(a)
                pass
            try:
                temp = db['Issue'][str(c["issueId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                RepoDoc = RepoIssueCollection.createEdge()
                RepoDoc["_key"] = (str(c["issueId"]) + str(c["repositoryId"])).replace("/", "@")
                RepoDoc.links(temp2, temp)
                RepoDoc.save()
            except Exception:
                pass

    repositories_queue = Queue(1500000)
    commits_queue = Queue(1500000)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(3)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(3)]
    for repository in queryResult:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


org = 'mundipagg'
RepoQuery(org)
dev(org)
Teams(org)
teamsDev(org)
teamsRepo(org)
readme(org)
languages(org)
commitcollector(org)
statscollector(org)
forkCollector(org)
issue(org)
