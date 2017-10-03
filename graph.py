from queue import Queue
from threading import Thread

import pyArango
from pyArango.collection import Collection, Field
from pyArango.connection import *

from graphqlclient import ClientRest
from graphqlclient import GraphQLClient

######conection info##########################################################
token = ''
url = 'https://api.github.com/graphql'
##############################################################################
number_of_repos = 50

client = GraphQLClient(url, token)
clientRest2 = ClientRest(token)


def restQuery(url, query, temp):
    result = clientRest2.execute(query=url + query + temp)
    return result
######## Classes #########################################################
class ContributedRepositories(pyArango.collection.Edges):
    _fields = dict(
    )


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
        size=Field()
    )

class RepoDev(pyArango.collection.Edges):
    _fields = dict(
    )

class Languages(Collection):
    """
    LANGUAGES
    """
    _fields = dict(
        language=Field(),
        id=Field()
    )

class Teams(Collection):
    """
    TEAMS
    """
    _fields = dict(
        createdAt=Field(),
        teamName=Field(),
        privacy=Field(),
        slug=Field(),
        childTeams=Field(),
        childTeamsTotal=Field(),
        ancestors=Field(),
        id=Field()
    )


class Commit(Collection):
    """
    COMMIT
    """
    _fields = dict(
        messageHeadline=Field(),
        oid=Field(),
        committedDate=Field(),
        author=Field(),
        devId=Field(),
        GitHubId=Field(),
        repositoryId=Field(),
        repoName=Field(),
        branchName=Field()
    )


class mentionableUsers(pyArango.collection.Edges):
    _fields = dict(
        aaa=Field(),
    )
class Teste(Collection):
    _fields = dict(
        repoName=Field(),
    )

class Dev(Collection):
    """
    DEV
    """
    _fields = dict(
        devName=Field(),
        login=Field(),
        avatar_url=Field(),
        followers=Field(),
        following=Field()
    )


class Repo(Collection):
    """
    REPO
    """
    _fields = dict(
        repoName=Field(),
        description=Field(),
        url=Field(),
        isPrivate=Field(),
        primaryLanguage=Field(),
        forks=Field(),
        stargazers=Field(),
        watchers=Field(),
        createdAt=Field(),
        id=Field(),
        nameWithOwner=Field()
    )

class Repo1(Collection):
    """
    REPO2
    """
    _fields = dict(
        repoName=Field(),
        description=Field(),
        url=Field(),
        isPrivate=Field(),
        primaryLanguage=Field(),
        forks=Field(),
        stargazers=Field(),
        watchers=Field(),
        createdAt=Field(),
        id=Field(),
        nameWithOwner=Field(),
        licenseId=Field(),
        Type=Field(),
        readme=Field()
    )
class Fork(Collection):
    """
    Fork
    """
    _fields = dict(
        repositoryId=Field(),
        repoName=Field(),
        createdAt=Field(),
        id=Field(),
        isPrivate=Field(),
        isLocked=Field(),
        devId=Field(),
        login=Field(),
        forkId=Field(),
        org=Field()
    )

class Issue(Collection):
    """
    Issue
    """
    _fields = dict(
        repositoryId=Field(),
        repoName=Field(),
        state=Field(),
        closedAt=Field(),
        author=Field(),
        issueId=Field(),
        createdAt=Field(),
        closed=Field(),
        label=Field(),
        title=Field(),
        org=Field()
    )


######pagination############################################################


def pagination(query2, number_of_repo, tmp, org):
    pag = client.execute(query2,
                         {
                             "number_of_repos": number_of_repo,
                             "next": tmp,
                             "org": org
                         })
    return pag


def paginationRepoNum(query2, tmp, num):
    pag = client.execute(query2,
                         {
                             "number_of_repos": num,
                             "next": tmp
                         })
    return pag


def paginationOrg(query2, tmp, num):
    pag = client.execute(query2,
                         {
                             "org": tmp,
                             "next": num
                         })
    return pag


def paginationSlug(query2, tmp, slugTemp, org):
    pag = client.execute(query2,
                         {
                             "number_of_repos": number_of_repos,
                             "next": tmp,
                             "slug": slugTemp,
                             "org": org
                         })
    return pag


def paginationNext(query2, next, next2):
    pag = client.execute(query2,
                         {
                             "number_of_repos": number_of_repos,
                             "next": next,
                             "next2": next2
                         })
    return pag


def paginatioOrgDate(query2, next, next2, org):
    pag = client.execute(query2,
                         {
                             "number_of_repos": number_of_repos,
                             "next": next,
                             "next2": next2,
                             "org": org
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

conn = Connection(username="root", password="")
try:
    db = conn.createDatabase(name="athena3")
except Exception:
    db = conn["athena3"]

# ##### Repo #######################################################################
def RepoQuery(org):
    query = '''
        query($number_of_repos:Int! $next:String, $org:String!)  {
          organization(login: $org) {
            repositories(first: $number_of_repos, after:$next) {
              edges {
                node {
                  defaultBranchRef{
                    target{
                      repository{
                        licenseInfo {
                         licenseId: id
                          licenseType: key
                        }
                      }
                    }
                  }
                  id
                  name
                  description
                  url
                  nameWithOwner
                  isPrivate
                  primaryLanguage {
                    priLanguage: name
                  }
                  forks{
                    totalCount
                  }
                  stargazers{
                    totalCount
                  }
                  watchers{
                     totalCount
                  }
                  createdAt
                }
                cursor
              }
            }
          }
        }
    '''
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
            prox = pagination(query, 100, cursor, org)
            proxRepositorios = prox["data"]["organization"]["repositories"]["edges"]
            for i in proxRepositorios:
                try:
                    count = count + 1
                    try:
                        doc = repoCollection[str(i["node"]["id"].replace("/", "@"))]
                    except:
                        doc = repoCollection.createDocument()
                        pass
                    doc['repoName'] = i["node"]["name"]
                    doc["description"] = i["node"]["description"]
                    doc["url"] = i["node"]["url"]
                    doc["openSource"] = False if i["node"]["isPrivate"] else True
                    doc["primaryLanguage"] = find('priLanguage', i)
                    doc["forks"] = i["node"]["forks"]["totalCount"]
                    doc["stargazers"] = i["node"]["stargazers"]["totalCount"]
                    doc["watchers"] = i["node"]["watchers"]["totalCount"]
                    doc["createdAt"] = i["node"]["createdAt"]
                    doc["nameWithOwner"] = i["node"]["nameWithOwner"]
                    doc["licenseId"] = find('licenseId', i)
                    print(i["node"]["name"])
                    doc["licenseType"] = find('licenseType', i)
                    doc["id"] = i["node"]["id"].replace("/", "@")
                    doc["org"] = org
                    doc._key = i["node"]["id"].replace("/", "@")
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

    query = '''
    query($number_of_repos:Int! $next:String, $org:String!){
      organization(login:$org) {
        members(first:$number_of_repos after:$next) {
          edges {
            node {
              id
              name
              followers (first:1){
                totalCount
                }
              following(first:1){
                totalCount
              }
              login
              avatarUrl
              contributedRepositories(last:1){
                  totalCount
              }
              pullRequests (last:1){
                  totalCount
              }
            }
            cursor
          }
        }
      }
    }
    '''

    count = 0
    first = True
    cursor = None
    while cursor or first:
        try:
            prox = pagination(query, 30, cursor, org)
            # print(prox)
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



###############################################################################################################



###### ContributedRepositories ##########################################################################################
def contributedRepositoriesCollection(org):
    try:
        ContributedRepositoriesCollection = db.createCollection("ContributedRepositories")
    except Exception:
        ContributedRepositoriesCollection = db["ContributedRepositories"]
    query = '''
    query($number_of_repos:Int! $next:String){
      organization(login:"stone-payments") {
        members(first:$number_of_repos after:$next) {
          edges {
            node {
              id
              contributedRepositories(first:100 affiliations:ORGANIZATION_MEMBER){
                edges{
                    node{
                      id
                    }
                    cursor
                  }
              }
            }
            cursor
          }
        }
      }
    }
    '''

    count = 0
    first = True
    cursor = None
    while cursor or first:
        try:
            prox = pagination(query, cursor)
            proxRepositorios = prox["data"]["organization"]["members"]["edges"]
            for i in proxRepositorios:
                proxNode = i["node"]["contributedRepositories"]["edges"]
                for j in proxNode:
                    try:
                        temp = db['Dev'][str(i["node"]["id"])]
                        temp2 = db['Repo'][str(j["node"]["id"])]
                        doc = ContributedRepositoriesCollection.createEdge({"aaa": 10})
                        doc.links(temp2, temp)
                        doc.save()
                    except Exception:
                        continue
            cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
            count = count + 1
        except Exception as a:
            print(a)
            cursor = False
            first = False
    print(count)


###### mentionableUsers #########################################################################################################
def mentionableUsers(org):
    try:
        mentionableUsersCollection = db.createCollection("mentionableUsers")
    except Exception:
        mentionableUsersCollection = db["mentionableUsers"]
    query = '''
    query($number_of_repos:Int! $next:String){
        organization(login:"stone-payments"){
        repositories(last:$number_of_repos after: $next){
          edges{
            node{
              name
              id
              mentionableUsers(last:100){
                edges{
                  node{
                    name
                    id
                  }
                }
              }
            }
            cursor
          }
        }
      }
    }
    '''

    count = 0
    first = True
    cursor = None
    while cursor or first:
        try:
            prox = pagination(query, cursor)
            proxRepositorios = prox["data"]["organization"]["repositories"]["edges"]
            for i in proxRepositorios:
                count = count + 1
                proxNode = i["node"]["mentionableUsers"]["edges"]
                for j in proxNode:
                    count = count + 1
                    try:
                        temp = db['Dev'][str(j["node"]["id"]).replace("/", "@")]
                        temp2 = db['Repo'][str(i["node"]["id"]).replace("/", "@")]
                        doc = mentionableUsersCollection.createEdge({"aaa": 10})
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception:
                        pass
            cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
        except Exception as a:
            print(a)
            cursor = False
            first = False
    print(count)


###### Teams #########################################################################################
def Teams(org):
    try:
        TeamsCollection = db.createCollection("Teams")
    except Exception:
        TeamsCollection = db["Teams"]
    db['Teams'].ensureHashIndex(['teamName'], unique=False, sparse=False)

    query = '''
    query($number_of_repos:Int! $next:String, $org:String!){
      organization(login: $org) {
        teams(first: $number_of_repos after: $next) {
          totalCount
          pageInfo {
            endCursor
          }
          edges {
            node {
              ancestors(first: 100) {
                nodes {
                  id
                  name
                }
              }
              members(first: 100) {
                totalCount
              }
              createdAt
              id
              name
              privacy
              slug
              childTeams(first: 100) {
                totalCount
                nodes {
                  name
                  id
                }
              }
            }
          }
        }
      }
    }
    '''

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

    query = '''
    query($number_of_repos:Int!, $next:String, $slug:String!, $org:String!){
      organization(login: $org) {
        team(slug: $slug) {
          name
          id
          members(first: $number_of_repos, after:  $next) {
            edges{
            node {
              name
              id
            }
            }
            pageInfo {
              endCursor
            }
          }
        }
      }
    }
    '''

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

    query = '''
        query ($number_of_repos: Int!, $next: String, $slug: String!, $org: String!) {
          organization(login: $org) {
            team(slug: $slug) {
              name
              id
              repositories(first: $number_of_repos, after: $next) {
                edges {
                  node {
                    id
                    name
                  }
                }
                pageInfo {
                  endCursor
                }
              }
            }
          }
        }
        '''

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

    print(queryResult)
    query = """
    query ($number_of_repos: Int!, $next: String, $next2: String!,$org:String!) {
      repository(owner: $org, name: $next2) {
        repositoryId: id
        languages(first: $number_of_repos after:$next) {
          pageInfo{
            endCursor
          }
          totalSize
          edges {
            size
            node {
              id
              name
            }
          }
        }
      }
    }
    """

    for repositoryname in queryResult:
        first = True
        cursor = None
        while cursor or first:
            first = False
            print(repositoryname)
            try:
                prox = paginatioOrgDate(query, cursor, repositoryname, org)
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
            query = '''
            query ($org: String!, $next: String!) {
              organization(login: $org) {
                repository(name: $next) {
                  id
                  defaultBranchRef {
                    target {
                      ... on Commit {
                        blame(path: "README.md") {
                          ranges {
                            endingLine
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            '''
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


urlCommit = 'https://api.github.com/repos/'


def commitcollector(org):
    try:
        db['Commit'].ensureHashIndex(['org'], unique=False, sparse=False)
    except Exception:
        pass
    try:
        commitCollection = db.createCollection["Commit"]
    except Exception:
        commitCollection = db["Commit"]
        pass
    try:
        DevCommitCollection = db.createCollection["DevCommit"]
    except:
        DevCommitCollection = db["DevCommit"]
        pass
    try:
        RepoCommitCollection = db.createCollection["RepoCommit"]
    except:
        RepoCommitCollection = db["RepoCommit"]
        pass
    try:
        RepoDevCollection = db.createCollection["RepoDev"]
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
            query = '''
    query($number_of_repos:Int!, $next:String, $next2:String!,$org:String!){
      repository(owner: $org, name: $next2) {
        repositoryId: id
        repoName: name
        defaultBranchRef {
          branchName: name
          target {
            ... on Commit {
              history(first: $number_of_repos, after: $next, since: "2017-09-15T00:00:00Z") {
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
    try:
        ForkCollection = db.createCollection["Fork"]
    except Exception:
        ForkCollection = db["Fork"]
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


def issue(org):
    try:
        db['Issue'].ensureHashIndex(['repoName'], unique=False, sparse=False)
        db['Issue'].ensureSkiplistIndex(['closedAt'], unique=False, sparse=False)
        db['Issue'].ensureSkiplistIndex(['createdAt'], unique=False, sparse=False)
    except Exception:
        pass
    try:
        IssueCollection = db.createCollection["Issue"]
    except Exception:
        IssueCollection = db["Issue"]
        pass
    try:
        RepoIssueCollection = db.createCollection["RepoIssue"]
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
            query = '''
    query($number_of_repos:Int!, $next:String, $next2:String!,$org:String!){
      organization(login: $org) {
        Org: login
        repository(name: $next2) {
          repositoryId: id
          repoName: name
          issues(first: $number_of_repos, after: $next) {
            pageInfo {
              endCursor
            }
            edges {
              node {
                state
                authorAssociation
                lastEditedAt
                timeline(last: 100) {
                  nodes {
                    ... on ClosedEvent {
                      closedAt: createdAt
                    }
                  }
                }
                author
                issueId: id
                createdAt
                closed
                labels(first: 1) {
                  edges {
                    node {
                      label:name
                    }
                  }
                }
                title
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


org = 'stone-payments'
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
