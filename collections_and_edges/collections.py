from queue import Queue
from threading import Thread
from module import *


# REPO ###############################


def repo_query(db, org):
    with open("queries/repoQuery.txt", "r") as query:
        query = query.read()
    repo_collection = db["Repo"]
    languages_collection = db["Languages"]
    languages_repo_collection = db["LanguagesRepo"]
    db['Repo'].ensureHashIndex(['repoName'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['isPrivate'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['licenseId'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['licenseType'], unique=False, sparse=False)

    has_next_page = True
    cursor = None
    while has_next_page:
        try:
            prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor, org=org)
            # print(prox)
            has_next_page = find('hasNextPage', prox)
            cursor = find('endCursor', prox)
            prox_repositorios = prox["data"]["organization"]["repositories"]["edges"]
            for repo in prox_repositorios:
                languages_repo = find('language_edges', repo)
                try:
                    try:
                        doc = repo_collection[str(repo["node"]["id"].replace("/", "@"))]
                    except Exception:
                        doc = repo_collection.createDocument()
                    doc['repoName'] = repo["node"]["name"]
                    doc["description"] = repo["node"]["description"]
                    doc["url"] = repo["node"]["url"]
                    doc["openSource"] = False if repo["node"]["isPrivate"] else True
                    doc["primaryLanguage"] = find('priLanguage', repo)
                    doc["forks"] = repo["node"]["forks"]["totalCount"]
                    doc["issues"] = repo["node"]["issues"]["totalCount"]
                    doc["stargazers"] = repo["node"]["stargazers"]["totalCount"]
                    doc["watchers"] = repo["node"]["watchers"]["totalCount"]
                    doc["createdAt"] = repo["node"]["createdAt"]
                    doc["nameWithOwner"] = repo["node"]["nameWithOwner"]
                    doc["licenseId"] = find('licenseId', repo)
                    doc["licenseType"] = find('licenseType', repo)
                    doc["id"] = repo["node"]["repoId"].replace("/", "@")
                    doc["org"] = org
                    doc._key = repo["node"]["repoId"].replace("/", "@")
                    doc.save()
                except Exception as exception:
                    handling_except(type(exception))
                for language in languages_repo:
                    # print(language)
                    try:
                        doc = languages_collection.createDocument()
                        doc["name"] = find('languageName', language)
                        doc["id"] = find('languageId', language)
                        doc._key = find('languageId', language).replace("/", "@")
                        doc.save()
                    except Exception as exception:
                        handling_except(type(exception))
                    try:
                        temp = db['Languages'][str(find('languageId', language)).replace("/", "@")]
                        temp2 = db['Repo'][str(find('repoId', repo)).replace("/", "@")]
                        doc = languages_repo_collection.createEdge(
                            {"size": round(((find('languageSize', language) / find('totalSize', repo)) * 100), 2)})
                        doc._key = (str(find('repoId', repo)) + str(find('languageId', language))).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(type(exception))
        except Exception:
            cursor = None


# DEV ###############################


def dev(db, org, query):
    dev_collection = db['Dev']
    first = True
    cursor = None
    while cursor or first:
        try:
            response = pagination_universal(query, number_of_repo=30, next_cursor=cursor, org=org)
            print(response)
            devs_edge = response["data"]["organization"]["members"]["edges"]
            for dev_slice in devs_edge:
                try:
                    try:
                        doc = dev_collection[str(dev_slice["node"]["id"].replace("/", "@"))]
                    except Exception:
                        doc = dev_collection.createDocument()
                    doc['devName'] = dev_slice["node"]["name"]
                    doc["followers"] = dev_slice["node"]["followers"]["totalCount"]
                    doc["following"] = dev_slice["node"]["following"]["totalCount"]
                    doc["login"] = dev_slice["node"]["login"]
                    doc["avatarUrl"] = dev_slice["node"]["avatarUrl"]
                    doc["contributedRepositories"] = dev_slice["node"]["contributedRepositories"]["totalCount"]
                    doc["pullRequests"] = dev_slice["node"]["pullRequests"]["totalCount"]
                    doc["id"] = dev_slice["node"]["id"].replace("/", "@")
                    doc["org"] = org
                    doc._key = dev_slice["node"]["id"].replace("/", "@")
                    doc.save()
                except Exception as exception:
                    handling_except(type(exception))
            cursor = devs_edge[len(devs_edge) - 1]["cursor"]
        except Exception:
            cursor = False
            first = False


# TEAMS ###############################


def teams(db, org):
    teams_collection = db["Teams"]
    teams_dev_collection = db["TeamsDev"]
    teams_repo_collection = db["TeamsRepo"]
    with open("queries/teamsQuery.txt", "r") as query:
        query = query.read()
    cursor = None
    has_next_page = True
    while has_next_page:
        try:
            prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor, org=org)
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
                    doc._key = team["node"]["id"].replace("/", "@")
                    doc.save()
                except Exception as exception:
                    handling_except(type(exception))
                for team_dev_content in team_dev_contents:
                    try:
                        temp = db['Dev'][str(find('memberId', team_dev_content)).replace("/", "@")]
                        temp2 = db['Teams'][str(team["node"]["id"]).replace("/", "@")]
                        doc = teams_dev_collection.createEdge()
                        doc._key = (str(team["node"]["id"]) + str(find('memberId', team_dev_content))).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(type(exception))
                for team_repo_content in team_repo_contents:
                    try:
                        temp = db['Repo'][str(find('repoId', team_repo_content)).replace("/", "@")]
                        temp2 = db['Teams'][str(team["node"]["id"]).replace("/", "@")]
                        doc = teams_repo_collection.createEdge()
                        doc._key = (str(team["node"]["id"]) + str(find('repoId', team_repo_content))).replace("/", "@")
                        doc.links(temp, temp2)
                        doc.save()
                    except Exception as exception:
                        handling_except(type(exception))
        except Exception:
            cursor = None


# LANGUAGES ###############################


def languages(db, org):
    languages_collection = db["Languages"]
    languages_repo_collection = db["LanguagesRepo"]
    with open("queries/languagesArango.txt", "r") as aql:
        aql = aql.read()
    bind_vars = {"org": org}
    query_result = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bind_vars)

    def collector(repositories: Queue, ):
        while True:
            repos = repositories.get_nowait()
            with open("queries/languagesQuery.txt", "r") as query:
                query = query.read()
            first = True
            cursor = None
            while cursor or first:
                first = False
                try:
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor,
                                                next_repo=repos, org=org)
                    print(prox)
                    cursor = find('endCursor', prox)
                    prox_node = find('languages', prox)
                    edges = find('edges', prox_node)
                    for node in edges:
                        try:
                            doc = languages_collection.createDocument()
                            doc["name"] = find('name', node)
                            doc["id"] = find('id', node)
                            doc._key = find('id', node).replace("/", "@")
                            doc.save()
                        except Exception as exception:
                            handling_except(type(exception))
                        try:
                            temp = db['Languages'][str(node["node"]["id"]).replace("/", "@")]
                            temp2 = db['Repo'][str(find('repositoryId', prox)).replace("/", "@")]
                            doc = languages_repo_collection.createEdge(
                                {"size": round(((node['size'] / find('totalSize', prox)) * 100), 2)})
                            doc._key = (str(node["node"]["id"]) + str(find('repositoryId', prox))).replace("/", "@")
                            doc.links(temp, temp2)
                            doc.save()
                        except Exception as exception:
                            handling_except(type(exception))
                except Exception:
                    cursor = False
                    first = False

    repositories_queue = Queue(queue_max_size)
    workers = [Thread(target=collector, args=(repositories_queue,)) for _ in range(num_of_threads)]
    for repository in query_result:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.join() for t in workers]

# COMMITS ###############################


def commit_collector(db, org):
    commit_collection = db["Commit"]
    dev_commit_collection = db["DevCommit"]
    repo_commit_collection = db["RepoCommit"]
    repo_dev_collection = db["RepoDev"]
    with open("queries/commitArango.txt", "r") as aql:
        aql = aql.read()
    bind_vars = {"org": org}
    query_result = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bind_vars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            first = True
            cursor = None
            with open("queries/commitQuery.txt", "r") as query:
                query = query.read()
            while cursor is not None or first:
                first = False
                try:
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor,
                                                next_repo=repository, org=org, since=since_time, until=until_time)
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
            c = commits_queue.get(timeout=commit_queue_timeout)
            try:
                try:
                    doc = commit_collection[str(c["commitId"].replace("/", "@"))]
                except Exception:
                    doc = commit_collection.createDocument()
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
            except Exception as exception:
                handling_except(type(exception))
            try:
                temp = db['Commit'][str(c["commitId"])]
                temp2 = db['Dev'][str(c["devId"])]
                commit_doc = dev_commit_collection.createEdge()
                commit_doc["_key"] = (str(c["commitId"]) + str(c["devId"])).replace("/", "@")
                commit_doc.links(temp2, temp)
                commit_doc.save()
            except Exception as exception:
                handling_except(type(exception))
            try:
                temp = db['Commit'][str(c["commitId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                repo_doc = repo_commit_collection.createEdge()
                repo_doc["_key"] = (str(c["commitId"]) + str(c["repositoryId"])).replace("/", "@")
                repo_doc.links(temp2, temp)
                repo_doc.save()
            except Exception as exception:
                handling_except(type(exception))
            try:
                temp = db['Dev'][str(c["devId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                dev_doc = repo_dev_collection.createEdge()
                dev_doc["_key"] = (str(c["repositoryId"]) + str(c["devId"])).replace("/", "@")
                dev_doc.links(temp2, temp)
                dev_doc.save()
            except Exception as exception:
                handling_except(type(exception))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    for repo in query_result:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# README ###############################

def readme(db, org):
    with open("queries/readmeArango.txt", "r") as aql:
        aql = aql.read()
    bind_vars = {"org": org}
    query_result = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bind_vars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repos = repositories.get_nowait()
            with open("queries/readmeQuery.txt", "r") as query:
                query = query.read()
            try:
                prox = pagination_universal(query, next_cursor=repos['repoName'], org=org)
                print(prox)
                output.put(1)
                if prox.get('errors'):
                    doc = db['Repo'][str(repos['key'])]
                    doc["readme"] = None
                    doc.save()
                    continue
                try:
                    ranges = find('ranges', prox)
                    doc = db["Repo"][str(find('id', prox))]
                    doc["readme"] = "OK" if ranges[-1]['endingLine'] >= 5 else "Poor"
                    doc.save()
                except Exception:
                    continue
            except Exception as exception:
                handling_except(type(exception))

    count_queue = Queue(queue_max_size)
    repositories_queue = Queue(queue_max_size)
    workers = [Thread(target=collector, args=(repositories_queue, count_queue)) for _ in range(num_of_threads)]
    for repository in query_result:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.join() for t in workers]


# STATS ###############################

def stats_collector(db, org):
    commit_collection = db["Commit"]
    with open("queries/statsQuery.txt", "r") as aql:
        aql = aql.read()
    bind_vars = {"org": org, "since_time": since_time, "until_time": until_time}
    query_result = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bind_vars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            try:
                temp = repository["oid"]
                query = org + "/" + repository["repo"] + '/commits/'
                result = clientRest2.execute(urlCommit, query, temp)
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
                handling_except(type(exception))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(stats_num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(stats_num_of_threads)]

    for repo in query_result:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# FORK ###############################


def fork_collector(db, org):
    fork_collection = db["Fork"]
    dev_fork_collection = db["DevFork"]
    repo_fork_collection = db["RepoFork"]
    with open("queries/forkArango.txt", "r") as aql:
        aql = aql.read()
    bind_vars = {"org": org}
    query_result = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bind_vars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            first = True
            cursor = None
            with open("queries/forkQuery.txt", "r") as query:
                query = query.read()
            while cursor is not None or first:
                first = False
                try:
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor,
                                                next_repo=repository, org=org)
                    print(prox)
                    if prox.get("documentation_url"):
                        print("ERROR")
                    cursor = find('endCursor', prox)
                    prox_node = find('repository', prox)
                    forks = find('edges', prox_node)
                    repository_id = prox_node["repositoryId"]
                    repo_name = prox_node["repoName"]

                    for c in forks:
                        node = c["node"]
                        author = node["owner"] or {'devId': 'anonimo', 'login': 'anonimo'}
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
                        output.put(commit)
                except Exception:
                    cursor = None
                    first = False

    def save(repositories: Queue, output: Queue):
        while True:
            c = commits_queue.get(timeout=queue_timeout)
            try:
                try:
                    doc = fork_collection[str(c["forkId"].replace("/", "@"))]
                except Exception:
                    doc = fork_collection.createDocument()
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
            except Exception as exception:
                handling_except(type(exception))
            try:
                temp = db['Fork'][str(c["forkId"])]
                temp2 = db['Dev'][str(c["devId"])]
                commit_doc = dev_fork_collection.createEdge()
                commit_doc["_key"] = (str(c["forkId"]) + str(c["devId"])).replace("/", "@")
                commit_doc.links(temp2, temp)
                commit_doc.save()
            except Exception as exception:
                handling_except(type(exception))
            try:
                temp = db['Fork'][str(c["forkId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                repo_doc = repo_fork_collection.createEdge()
                repo_doc["_key"] = (str(c["forkId"]) + str(c["repositoryId"])).replace("/", "@")
                repo_doc.links(temp2, temp)
                repo_doc.save()
            except Exception as exception:
                handling_except(type(exception))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    for repo in query_result:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# ISSUES ###############################


def issue(db, org):
    issue_collection = db["Issue"]
    repo_issue_collection = db["RepoIssue"]
    with open("queries/issueArango.txt", "r") as aql:
        aql = aql.read()
    bind_vars = {"org": org}
    query_result = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bind_vars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repository = repositories.get_nowait()
            first = True
            cursor = None
            with open("queries/issueQuery.txt", "r") as query:
                query = query.read()
            while cursor is not None or first:
                first = False
                try:
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next_cursor=cursor,
                                                next_repo=repository, org=org)
                    print(prox)
                    if prox.get("documentation_url"):
                        print("ERROR")
                    cursor = find('endCursor', prox)
                    prox_node = find('repository', prox)
                    issues = find('edges', prox_node)
                    repository_id = prox_node["repositoryId"]
                    repo_name = prox_node["repoName"]

                    for node in issues:
                        commit = {
                            "repositoryId": repository_id,
                            "repoName": repo_name,
                            "state": find('state', node),
                            "closed_login": find('closed_login', node),
                            "closedAt": find('closedAt', node),
                            "issueId": find('issueId', node),
                            "created_login": find('created_login', node),
                            "createdAt": find('createdAt', node),
                            "authorAssociation": find('authorAssociation', node),
                            "closed": find('closed', node),
                            "label": find('label', node),
                            "title": find('title', node),
                            "org": org
                        }
                        output.put(commit)
                except Exception:
                    cursor = None
                    first = False

    def save(repositories: Queue, output: Queue):
        while True:
            c = commits_queue.get(timeout=queue_timeout)
            try:
                try:
                    doc = issue_collection[str(c["issueId"].replace("/", "@"))]
                except Exception:
                    doc = issue_collection.createDocument()
                doc["repositoryId"] = c["repositoryId"]
                doc["repoName"] = c["repoName"]
                doc["state"] = c["state"]
                doc["closed_login"] = c["closed_login"]
                doc["closedAt"] = c["closedAt"]
                doc["issueId"] = c["issueId"]
                doc["created_login"] = c["created_login"]
                doc["createdAt"] = c["createdAt"]
                doc["authorAssociation"] = c["authorAssociation"]
                doc["closed"] = c["closed"]
                doc["label"] = c["label"]
                doc["title"] = c["title"]
                doc["org"] = c["org"]
                doc._key = c["issueId"].replace("/", "@")
                doc.save()
            except Exception as exception:
                handling_except(type(exception))
            try:
                temp = db['Issue'][str(c["issueId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                repo_doc = repo_issue_collection.createEdge()
                repo_doc["_key"] = (str(c["issueId"]) + str(c["repositoryId"])).replace("/", "@")
                repo_doc.links(temp2, temp)
                repo_doc.save()
            except Exception as exception:
                handling_except(type(exception))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    for repo in query_result:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]
