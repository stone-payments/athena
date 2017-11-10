from threading import Thread
from module import *


# REPO ###############################

def repo2(db, org, query, collection_name, edge_name):

    def content(self, response, node):
        readme_ranges = find('ranges', node)
        if readme_ranges:
            readme = "OK" if readme_ranges[-1]['endingLine'] >= 5 else "Poor"
        else:
            readme = None
        save_content = {
            "collection_name": collection_name[0],
            "_id": node["node"]["repoId"].replace("/", "@"),
            "repoName": node["node"]["name"],
            "description": node["node"]["description"],
            "url": node["node"]["url"],
            "openSource": False if node["node"]["isPrivate"] else True,
            "primaryLanguage": find('priLanguage', node),
            "forks": node["node"]["forks"]["totalCount"],
            "issues": node["node"]["issues"]["totalCount"],
            "stargazers": node["node"]["stargazers"]["totalCount"],
            "watchers": node["node"]["watchers"]["totalCount"],
            "createdAt": node["node"]["createdAt"],
            "nameWithOwner": node["node"]["nameWithOwner"],
            "licenseId": find('licenseId', node),
            "licenseType": find('licenseType', node),
            "readme": readme,
            "org": self.org,
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')),
            "languages": parse_multiple_languages(node, "language_edges", "languageName",
                                                  "languageSize"),
            "committed_today": False if find('committedDate', node) is None else True
        }
        return save_content

    def edges(node, response):
        save_edges = [
        ]
        return save_edges

    start = Collector(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                      number_of_repo=repo_number_of_repos, since=since_time, until=until_time,
                      save_content=content, save_edges=edges)
    start.start()


# DEV ###############################


def dev2(db, org, query, collection_name, edge_name):

    def content(self, response, node):
        save_content = {
            "collection_name": collection_name[0],
            "_id": find("id", node),
            "devName": find("name", node),
            "followers": node["node"]["followers"]["totalCount"],
            "following": node["node"]["following"]["totalCount"],
            "login": node["node"]["login"],
            "avatarUrl": node["node"]["avatarUrl"],
            "org": self.org,
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')),
        }
        return save_content

    def edges(node, response):
        save_edges = [
        ]
        return save_edges

    start = Collector(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                      number_of_repo=repo_number_of_repos, since=since_time, until=until_time,
                      save_content=content, save_edges=edges)
    start.start()


# TEAMS ###############################


def teams2(db, org, query, collection_name, edge_name):
    # def id_content(node):
    #     id = [{"_id": node["node"]["id"].replace("/", "@")}]
    #     return id

    def content(self, response, node):
        save_content = {
            "collection_name": collection_name[0],
            'createdAt': node["node"]["createdAt"],
            "teamName": node["node"]["name"],
            "privacy": node["node"]["privacy"],
            "slug": node["node"]["slug"],
            "membersCount": find('membersCount', node),
            "repoCount": find('repoCount', node),
            "_id": find('teamId', node),
            "org": self.org,
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        }
        return save_content

    # def edges(node, response):
    #     save_edges = [{
    #         "edge_name": "team_dev",
    #         "to": find('memberId', node),
    #         "from": find('teamId', response),
    #         "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    #     }
    #     ]
    #     return save_edges

    def edges(team, members, repos):
        collect_member_of_team = [
            {
                "edge_name": "dev_to_team",
                'to': find('_id', team),
                'from': find('memberId', member),
                "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
            }
            for member in members
        ]
        collect_repositories_of_team = [
            {
                "edge_name": "_to_team",
                'to': find('_id', team),
                'from': find('repoId', repo),
                "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
            }
            for repo in repos
        ]
        return collect_member_of_team, collect_repositories_of_team

    start = Collector(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                      number_of_repo=repo_number_of_repos, since=since_time, until=until_time,
                      save_content=content, save_edges=edges)
    start.start_team()


def teams(db, org, query):
    teams_collection = db["Teams"]
    teams_dev_collection = db["TeamsDev"]
    teams_repo_collection = db["TeamsRepo"]
    cursor = None
    has_next_page = True
    while has_next_page:
        try:
            prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor, org=org)
            limit_validation(rate_limit=find('rateLimit', prox))
            print(prox)
            cursor = find('endCursor', prox)
            has_next_page = find('hasNextPage', prox)
            print(has_next_page)
            proxrepositorios = prox["data"]["organization"]["teams"]["edges"]
            for team in proxrepositorios:
                team_dev_contents = find('members_edge', team)
                team_repo_contents = find('repo_edge', team)
                try:
                    doc = teams_collection[str(team["node"]["id"].replace("/", "@"))]
                except Exception:
                    doc = teams_collection.createDocument()
                try:
                    doc['createdAt'] = team["node"]["createdAt"]
                    doc["teamName"] = team["node"]["name"]
                    doc["privacy"] = team["node"]["privacy"]
                    doc["slug"] = team["node"]["slug"]
                    doc["membersCount"] = find('membersCount', team)
                    doc["repoCount"] = find('repoCount', team)
                    doc["id"] = team["node"]["id"].replace("/", "@")
                    doc["org"] = org
                    doc["db_last_updated"] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
                    doc._key = team["node"]["id"].replace("/", "@")
                    doc.save()
                except Exception as exception:
                    handling_except(exception)
                for team_dev_content in team_dev_contents:
                    try:
                        doc = teams_dev_collection[(str(team["node"]["id"]) +
                                                    str(find('memberId', team_dev_content))).replace("/", "@")]
                    except Exception:
                        doc = teams_dev_collection.createEdge()
                    try:
                        temp = db['Dev'][str(find('memberId', team_dev_content)).replace("/", "@")]
                        temp2 = db['Teams'][str(team["node"]["id"]).replace("/", "@")]
                        doc["db_last_updated"] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
                        doc._key = (str(team["node"]["id"]) + str(find('memberId', team_dev_content))).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(exception)
                for team_repo_content in team_repo_contents:
                    try:
                        doc = teams_repo_collection[(str(team["node"]["id"]) +
                                                     str(find('repoId', team_repo_content))).replace("/", "@")]
                    except Exception:
                        doc = teams_repo_collection.createEdge()
                    try:
                        temp = db['Repo'][str(find('repoId', team_repo_content)).replace("/", "@")]
                        temp2 = db['Teams'][str(team["node"]["id"]).replace("/", "@")]
                        doc["db_last_updated"] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
                        doc._key = (str(team["node"]["id"]) + str(find('repoId', team_repo_content))).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(exception)
        except Exception as exception:
            handling_except(exception)


# COMMITS ###############################

def commit_collector2(db, org, query, query_db, collection_name, edges_name):
    def content(self, response, node):
        save_content = {
            "collection_name": collection_name[0],
            "_id": find('commitId', node),
            "repositoryId": find('repositoryId', response),
            "repoName": find('repoName', response),
            "branchName": find('branchName', response),
            "messageHeadline": find('messageHeadline', node),
            "oid": find('oid', node),
            "committedDate": find('committedDate', node),
            "author": find('login', node),
            "devId": find('devId', node),
            "commitId": find('commitId', node),
            "org": self.org
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "commit_dev",
            "to": find('commitId', node),
            "from": find('devId', node)
        },
            {
                "edge_name": "commit_repo",
                "to": find('commitId', node),
                "from": find('repositoryId', node)
            },
            {
                "edge_name": "dev_repo",
                "to": find('devId', node),
                "from": find('repositoryId', node)
            }
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edges_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start()


# STATS ###############################

def stats_collector2(db, org, stats_query, collection_name, edges_name):
    def content(node, commit_id):
        save_content = {
            "collection_name": collection_name[0],
            "_id": commit_id,
            'totalAddDel': node['stats']['total'],
            'additions': node['stats']['additions'],
            'deletions': node['stats']['deletions'],
            'numFiles': len(node['files'])
        }
        return save_content

    def edges(node):
        save_edges = [
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edges_name, query_db=stats_query,
                            number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start_stats()


def stats_collector(db, org, query):
    commit_collection = db["Commit"]
    bind_vars = {"org": org, "since_time": since_time, "until_time": until_time}
    query_result = db.AQLQuery(query, batchSize=batch_size, rawResults=True, bindVars=bind_vars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            try:
                temp = repository["oid"]
                rest_query = org + "/" + repository["repo"] + '/commits/'
                result = clientRest2.execute(urlCommit, rest_query, temp)
                print(result)
            except Exception:
                continue
            commit = {
                "commitId": repository["id"],
                'totalAddDel': result['stats']['total'],
                'additions': result['stats']['additions'],
                'deletions': result['stats']['deletions'],
                'numFiles': len(result['files'])
            }
            output.put(commit)

    def save(repositories: Queue, output: Queue):
        while True:
            c = commits_queue.get(timeout=stats_queue_timeout)
            try:
                doc = commit_collection[str(c["commitId"].replace("/", "@"))]
                doc['totalAddDel'] = c['totalAddDel']
                doc['additions'] = c['additions']
                doc['deletions'] = c['deletions']
                doc['numFiles'] = c['numFiles']
                doc._key = c["commitId"].replace("/", "@")
                doc.save()
            except Exception as exception:
                handling_except(exception)

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(stats_num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(stats_num_of_threads)]

    for repo in query_result:
        print(repo)
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# FORK ###############################

def fork_collector2(db, org, query, query_db, collection_name, edges_name):
    def content(self, response, node):
        save_content = {
            "collection_name": collection_name[0],
            "repositoryId": find('repositoryId', response),
            "repoName": find('repoName', response),
            "createdAt": find('createdAt', node),
            "_id": find('forkId', node),
            "isPrivate": find('isPrivate', node),
            "isLocked": find('isLocked', node),
            "devId": find('devId', node),
            "login": find('login', node),
            "org": self.org
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "fork_to_dev",
            "to": find('_id', node),
            "from": find('devId', node),
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        },
            {
                "edge_name": "fork_to_repo",
                "to": find('_id', node),
                "from": find('repositoryId', node),
                "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
            }
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edges_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start_fork()


# ISSUES ###############################

def issue2(db, org, query, query_db, collection_name, edges_name):
    def content(self, response, node):
        save_content = {
            "collection_name": collection_name[0],
            "repositoryId": find('repositoryId', response),
            "repoName": find('repoName', response),
            "state": find('state', node),
            "closed_login": find('closed_login', node),
            "closedAt": find('closedAt', node),
            "_id": find('issueId', node),
            "created_login": find('created_login', node),
            "createdAt": find('createdAt', node),
            "authorAssociation": find('authorAssociation', node),
            "closed": find('closed', node),
            "label": find('label', node),
            "title": find('title', node),
            "org": self.org
        }
        return save_content

    def edges(node):
        save_edges = [
            {
                "edge_name": "issue_to_repo",
                "to": find('_id', node),
                "from": find('repositoryId', node),
                "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
            }
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edges_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start_fork()
