from module import *


# TEAMS_DEV ###############################


def teams_dev(db, org, query_arango, query_graphql):
    teams_dev_collection = db["TeamsDev"]
    bind_vars = {"org": org}
    query_result = db.AQLQuery(query_arango, rawResults=True, bindVars=bind_vars)
    for x in query_result:
        cursor = None
        has_next_page = True
        while has_next_page:
            try:
                prox = pagination_universal(query_graphql, number_of_repo=number_of_repos, next_cursor=cursor, slug=x,
                                            org=org)
                limit_validation(rate_limit=find('rateLimit', prox))
                print(prox)
                cursor = find('endCursor', prox)
                has_next_page = find('hasNextPage', prox)
                prox_node = prox["data"]["organization"]["team"]
                teams = prox_node["members"]["edges"]
                for team in teams:
                    try:
                        doc = teams_dev_collection[(str(team["node"]["id"]) +
                                                    str(prox_node["id"])).replace("/", "@")]
                    except Exception:
                        doc = teams_dev_collection.createEdge()
                    try:
                        temp = db['Dev'][str(team["node"]["id"]).replace("/", "@")]
                        temp2 = db['Teams'][str(prox_node["id"]).replace("/", "@")]
                        doc["db_last_updated"] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
                        doc._key = (str(team["node"]["id"]) + str(prox_node["id"])).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(exception)
            except Exception as exception:
                handling_except(exception)


# TEAMS_REPO ###############################


def teams_repo(db, org, query_arango, query_graphql):
    teams_repo_collection = db["TeamsRepo"]
    bind_vars = {"org": org}
    query_result = db.AQLQuery(query_arango, rawResults=True, bindVars=bind_vars)
    for x in query_result:
        cursor = None
        has_next_page = True
        while has_next_page:
            try:
                prox = pagination_universal(query_graphql, number_of_repo=number_of_repos, next_cursor=cursor, slug=x,
                                            org=org)
                print(prox)
                limit_validation(rate_limit=find('rateLimit', prox))
                cursor = find('endCursor', prox)
                has_next_page = find('hasNextPage', prox)
                prox_node = prox["data"]["organization"]["team"]
                teams = prox_node["repositories"]["edges"]
                for team in teams:
                    try:
                        doc = teams_repo_collection[(str(team["node"]["id"]) +
                                                     str(prox_node["id"])).replace("/", "@")]
                    except Exception:
                        doc = teams_repo_collection.createEdge()
                    try:
                        temp = db['Repo'][str(team["node"]["id"]).replace("/", "@")]
                        temp2 = db['Teams'][str(prox_node["id"]).replace("/", "@")]
                        doc["db_last_updated"] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
                        doc._key = (str(team["node"]["id"]) + str(prox_node["id"])).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(exception)
            except Exception as exception:
                handling_except(exception)
