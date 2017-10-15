from module import *


# TEAMS_DEV ###############################


def teams_dev(db, org):
    teams_dev_collection = db["TeamsDev"]
    bind_vars = {"org": org}
    with open("queries/teamsDevArango.txt", "r") as aql:
        aql = aql.read()
    query_result = db.AQLQuery(aql, rawResults=True, bindVars=bind_vars)
    with open("queries/teamsDevQuery.txt", "r") as query:
        query = query.read()
    for x in query_result:
        first = True
        cursor = None
        while cursor or first:
            try:
                prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor, slug=x, org=org)
                print(prox)
                prox_node = prox["data"]["organization"]["team"]
                teams = prox_node["members"]["edges"]
                for team in teams:
                    try:
                        temp = db['Dev'][str(team["node"]["id"]).replace("/", "@")]
                        temp2 = db['Teams'][str(prox_node["id"]).replace("/", "@")]
                        doc = teams_dev_collection.createEdge()
                        doc._key = (str(team["node"]["id"]) + str(prox_node["id"])).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(type(exception))
                cursor = prox["data"]["organization"]["team"]["members"]["pageInfo"]["endCursor"]
                if cursor is None:
                    cursor = False
            except Exception:
                cursor = False
                first = False


# TEAMS_REPO ###############################


def teams_repo(db, org):
    teams_repo_collection = db["TeamsRepo"]
    bind_vars = {"org": org}
    with open("queries/teamsRepoArango.txt", "r") as aql:
        aql = aql.read()
    query_result = db.AQLQuery(aql, rawResults=True, bindVars=bind_vars)
    with open("queries/teamsRepoQuery.txt", "r") as query:
        query = query.read()
    for x in query_result:
        first = True
        cursor = None
        while cursor or first:
            try:
                prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor, slug=x, org=org)
                print(prox)
                prox_node = prox["data"]["organization"]["team"]
                teams = prox_node["repositories"]["edges"]
                for team in teams:
                    try:
                        temp = db['Repo'][str(team["node"]["id"]).replace("/", "@")]
                        temp2 = db['Teams'][str(prox_node["id"]).replace("/", "@")]
                        doc = teams_repo_collection.createEdge()
                        doc._key = (str(team["node"]["id"]) + str(prox_node["id"])).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(type(exception))
                cursor = prox["data"]["organization"]["team"]["repositories"]["pageInfo"]["endCursor"]
                if cursor is None:
                    cursor = False
            except Exception:
                cursor = False
                first = False
