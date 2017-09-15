from threading import Thread

import pyArango
from pyArango.collection import Collection, Field
from pyArango.connection import *

from graphqlclient import GraphQLClient

######conection info##########################################################
token = '117d1985b8c852c7ecbd9980d16568ed023479ed'
url = 'https://api.github.com/graphql'
##############################################################################
number_of_repos = 50
client = GraphQLClient(url, token)


######## Classes #########################################################
class ContributedRepositories(pyArango.collection.Edges):
    _fields = dict(
        aaa=Field(),
    )


class TeamsDev(pyArango.collection.Edges):
    _fields = dict(
        aaa=Field(),
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

######pagination############################################################


def pagination(query2, number_of_repos, tmp, org):
    pag = client.execute(query2,
                         {
                             "number_of_repos": number_of_repos,
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

def paginationSlug(query2, tmp, slugTemp):
    pag = client.execute(query2,
                         {
                             "number_of_repos": number_of_repos,
                             "next": tmp,
                             "slug": slugTemp
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
# db = conn.createDatabase(name="athena3")
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

    # repoCollection = db.createCollection("Repo")
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
                    doc["licenseId"] = True if find('licenseId', i) is not None else False
                    print(i["node"]["name"])
                    doc["licenseType"] = True if find('licenseType', i) is not None else False
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
devCollection = db.createCollection('Dev')
db['Dev'].ensureHashIndex(['devName'], unique=False, sparse=False)
db['Dev'].ensureHashIndex(['login'], unique=False, sparse=False)

query = '''
query($number_of_repos:Int! $next:String){
  organization(login:"stone-payments") {
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
        prox = pagination(query, cursor)
        proxRepositorios = prox["data"]["organization"]["members"]["edges"]
        for i in proxRepositorios:
            count = count + 1
            doc = devCollection.createDocument()
            doc['devName'] = i["node"]["name"]
            doc["followers"] = i["node"]["followers"]["totalCount"]
            doc["following"] = i["node"]["following"]["totalCount"]
            doc["login"] = i["node"]["login"]
            doc["avatarUrl"] = i["node"]["avatarUrl"]
            doc["contributedRepositories"] = i["node"]["contributedRepositories"]["totalCount"]
            doc["pullRequests"] = i["node"]["pullRequests"]["totalCount"]
            doc["id"] = i["node"]["id"].replace("/", "@")
            doc._key = i["node"]["id"].replace("/", "@")
            doc.save()
        cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
    except Exception:
        cursor = False
        first = False
print(count)

###############################################################################################################



###### ContributedRepositories ##########################################################################################
ContributedRepositoriesCollection = db.createCollection("ContributedRepositories")

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
mentionableUsersCollection = db.createCollection("mentionableUsers")

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
TeamsCollection = db.createCollection("Teams")
db['Teams'].ensureHashIndex(['teamName'], unique=False, sparse=False)

query = '''
query($number_of_repos:Int! $next:String){
  organization(login: "stone-payments") {
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
while cursor or first:
    try:
        prox = pagination(query, cursor)
        proxRepositorios = prox["data"]["organization"]["teams"]["edges"]
        for i in proxRepositorios:
            count = count + 1
            doc = TeamsCollection.createDocument()
            doc['createdAt'] = i["node"]["createdAt"]
            doc["teamName"] = i["node"]["name"]
            doc["privacy"] = i["node"]["privacy"]
            doc["slug"] = i["node"]["slug"]
            doc["childTeams"] = i["node"]["childTeams"]["nodes"]
            doc["childTeamsTotal"] = i["node"]["childTeams"]["totalCount"]
            doc["ancestors"] = i["node"]["ancestors"]["nodes"]
            doc["id"] = i["node"]["id"].replace("/", "@")
            doc._key = i["node"]["id"].replace("/", "@")
            doc.save()
        cursor = prox["data"]["organization"]["teams"]["pageInfo"]["endCursor"]
    except Exception:
        cursor = False
        first = False
print(count)

###### TeamsDev #########################################################################################################
TeamsDevCollection = db.createCollection("TeamsDev")

aql = "FOR Team in Teams return Team.slug"
# by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
queryResult = db.AQLQuery(aql, rawResults=True)

query = '''
query($number_of_repos:Int!, $next:String, $slug:String!){
  organization(login: "stone-payments") {
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
            prox = paginationSlug(query, cursor, x)
            proxNode = prox["data"]["organization"]["team"]
            i = proxNode["members"]["edges"]
            for j in i:
                count = count + 1
                try:
                    temp = db['Dev'][str(j["node"]["id"]).replace("/", "@")]
                    print(temp)
                    temp2 = db['Teams'][str(proxNode["id"]).replace("/", "@")]
                    print(temp2)
                    doc = TeamsDevCollection.createEdge({"aaa": 10})
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

###### TeamsDev #########################################################################################################
# commitCollection = db.createCollection("Commit")

aql = "FOR Repo in Repo return Repo.repoName"
# by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True)

print(queryResult)
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


# for x in queryResult:
def commitrequest(repositoryname):
    first = True
    cursor = None
    while cursor or first:
        try:
            prox = paginationNext(query, cursor, repositoryname)
            cursor = prox["data"]["repository"]["defaultBranchRef"]["target"]["history"]["pageInfo"]["endCursor"]
            proxNode = prox["data"]["repository"]
            j = proxNode["defaultBranchRef"]["target"]["history"]["edges"]
            for i in j:
                try:
                    doc = commitCollection.createDocument()
                    doc["repositoryId"] = proxNode["repositoryId"]
                    doc["repoName"] = proxNode["repoName"]
                    doc["branchName"] = proxNode["defaultBranchRef"]["branchName"]
                    doc["messageHeadline"] = i["node"]["messageHeadline"]
                    doc["oid"] = i["node"]["oid"]
                    doc["committedDate"] = i["node"]["committedDate"]
                    doc["author"] = i["node"]["author"]["user"]["login"]
                    doc["devId"] = i["node"]["author"]["user"]["devId"]
                    doc["GitHubId"] = i["node"]["commitId"]
                    doc._key = i["node"]["commitId"].replace("/", "@")
                    doc.save()
                except Exception:
                    pass
            if cursor is None:
                cursor = False
        except Exception as a:
            print(a)
            cursor = False
            first = False
    return


if __name__ == '__main__':
    jobs = []
    count = 0
    for x in queryResult:
        count = count + 1
        p = Thread(target=commitrequest, args=(x,))
        jobs.append(p)
        p.start()
        print(count)

testeCollection = db.createCollection("Teste")
doc = testeCollection.createDocument()
doc['repoName'] = [
    {
        "size": 10093,
        "language": {
            "id": "MDg6TGFuZ3VhZ2UzMDg=",
            "name": "CSS"
        }
    },
    {
        "size": 387,
        "language": {
            "id": "MDg6TGFuZ3VhZ2UxNDA=",
            "name": "JavaScript"
        }
    }
]
doc._key = 'fafa5454085'
doc.save()

##### Languages #########################################################################################################
LanguagesCollection = db.createCollection("Languages")
LanguagesRepoCollection = db.createCollection("LanguagesRepo")
LanguagesCollection = db["Languages"]
LanguagesRepoCollection = db["LanguagesRepo"]
db['Languages'].ensureHashIndex(['name'], unique=True, sparse=False)

aql = "FOR Repo in Repo return Repo.repoName"
# by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True)

print(queryResult)
query = """
query ($number_of_repos: Int!, $next: String, $next2: String!) {
  repository(owner: "stone-payments", name: $next2) {
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
            prox = paginationNext(query, cursor, repositoryname)
            print(prox)
            cursor = find('endCursor', prox)
            print(cursor)
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

aql = "FOR Repo in Repo return {repoName:Repo.repoName,key:Repo._key}"
# by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
queryResult = db.AQLQuery(aql, batchSize=20000, rawResults=True)

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

# repoCollection = db.createCollection("Repo1")
repoCollection = db["Repo"]

db['Repo'].ensureHashIndex(['readme'], unique=False, sparse=False)

count = 0

for repo in queryResult:
    count = count + 1
    try:
        prox = paginationOrg(query, 'stone-payments', repo['repoName'])
        if prox.get('errors'):
            doc = db['Repo'][str(repo['key'])]
            doc["readme"] = False
            doc.save()
            continue
        try:
            a = find('ranges', prox)
            doc = db["Repo"][str(find('id', prox))]
            doc["readme"] = True if a[-1]['endingLine'] >= 5 else False
            doc.save()
        except Exception:
            continue
    except Exception as a:
        pass
    print(count)

RepoQuery("pagarme")
