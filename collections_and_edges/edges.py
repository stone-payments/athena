from module import *


###### TeamsDev #########################################################################################################


def teamsDev(db, org):
    TeamsDevCollection = db["TeamsDev"]
    bindVars = {"org": org}
    aql = "FOR Teams in Teams FILTER Teams.org == @org return Teams.slug"
    queryResult = db.AQLQuery(aql, rawResults=True, bindVars=bindVars)
    with open("queries/teamsDevQuery.txt", "r") as query:
        query = query.read()
    for x in queryResult:
        first = True
        cursor = None
        while cursor or first:
            try:
                prox = paginationuniversal(query, number_of_repo=number_of_repos, next=cursor, slug=x, org=org)
                print(prox)
                proxNode = prox["data"]["organization"]["team"]
                teams = proxNode["members"]["edges"]
                for team in teams:
                    try:
                        temp = db['Dev'][str(team["node"]["id"]).replace("/", "@")]
                        temp2 = db['Teams'][str(proxNode["id"]).replace("/", "@")]
                        doc = TeamsDevCollection.createEdge()
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception:
                        pass
                cursor = prox["data"]["organization"]["team"]["members"]["pageInfo"]["endCursor"]
                if cursor is None:
                    cursor = False
            except Exception:
                cursor = False
                first = False


# #### teamsRepo #######################################################################


def teamsRepo(db, org):
    TeamsRepoCollection = db["TeamsRepo"]
    bindVars = {"org": org}
    aql = "FOR Teams in Teams FILTER Teams.org == @org return Teams.slug"
    queryResult = db.AQLQuery(aql, rawResults=True, bindVars=bindVars)
    with open("queries/teamsRepoQuery.txt", "r") as query:
        query = query.read()
    for x in queryResult:
        first = True
        cursor = None
        while cursor or first:
            try:
                prox = paginationuniversal(query, number_of_repo=number_of_repos, next=cursor, slug=x, org=org)
                print(prox)
                proxNode = prox["data"]["organization"]["team"]
                teams = proxNode["repositories"]["edges"]
                for team in teams:
                    try:
                        temp = db['Repo'][str(team["node"]["id"]).replace("/", "@")]
                        temp2 = db['Teams'][str(proxNode["id"]).replace("/", "@")]
                        doc = TeamsRepoCollection.createEdge()
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception:
                        pass
                cursor = prox["data"]["organization"]["team"]["repositories"]["pageInfo"]["endCursor"]
                if cursor is None:
                    cursor = False
            except Exception:
                cursor = False
                first = False
