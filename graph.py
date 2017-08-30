import pyArango
from pyArango.collection import Collection, Field
from pyArango.connection import *

from graphqlclient import GraphQLClient

######conection info##########################################################
token = '986264e209f19220047de58e01f643329128cb36'
url = 'https://api.github.com/graphql'
##############################################################################
number_of_repos = 100
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
        id=Field(),
    )


class mentionableUsers(pyArango.collection.Edges):
    _fields = dict(
        aaa=Field(),
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


######pagination############################################################


def pagination(query2, tmp):
    pag = client.execute(query2,
                         {
                             "number_of_repos": number_of_repos,
                             "next": tmp
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


### Connection #####################################################################

conn = Connection(username="root", password="")
# db = conn.createDatabase(name="athena3")
db = conn["athena3"]

##### Repo #######################################################################
query = '''
    query($number_of_repos:Int! $next:String) {
      organization(login:"stone-payments") {
        repositories(first: $number_of_repos after: $next) {
          edges {
            node {
              id
              name 
              description
              url
              nameWithOwner
              isPrivate
              primaryLanguage {
                name
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

repoCollection = db.createCollection("Repo")

count = 0
first = True
cursor = None
while cursor or first:
    try:
        prox = pagination(query, cursor)
        proxRepositorios = prox["data"]["organization"]["repositories"]["edges"]
        for i in proxRepositorios:
            count = count + 1
            doc = repoCollection.createDocument()
            doc['repoName'] = i["node"]["name"]
            doc["description"] = i["node"]["description"]
            doc["url"] = i["node"]["url"]
            doc["isPrivate"] = i["node"]["isPrivate"]
            doc["primaryLanguage"] = i["node"]["primaryLanguage"]
            doc["forks"] = i["node"]["forks"]["totalCount"]
            doc["stargazers"] = i["node"]["stargazers"]["totalCount"]
            doc["watchers"] = i["node"]["watchers"]["totalCount"]
            doc["createdAt"] = i["node"]["createdAt"]
            doc["nameWithOwner"] = i["node"]["nameWithOwner"]
            doc["id"] = i["node"]["id"].replace("/", "@")
            doc._key = i["node"]["id"].replace("/", "@")
            doc.save()
        cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
    except Exception:
        cursor = False
        first = False
print(count)

###### Dev #########################################################################################################
devCollection = db.createCollection('Dev')

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
