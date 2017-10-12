from queue import Queue
from threading import Thread

from module import *


# REPO ###############################


def repo_query(db, org):
    with open("queries/repoQuery.txt", "r") as query:
        query = query.read()
    repoCollection = db["Repo"]
    db['Repo'].ensureHashIndex(['repoName'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['isPrivate'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['licenseId'], unique=False, sparse=False)
    db['Repo'].ensureHashIndex(['licenseType'], unique=False, sparse=False)

    first = True
    cursor = None
    while cursor or first:
        try:
            prox = pagination_universal(query, number_of_repo=number_of_repos, next=cursor, org=org)
            print(prox)
            proxRepositorios = prox["data"]["organization"]["repositories"]["edges"]
            for repo in proxRepositorios:
                try:
                    try:
                        doc = repoCollection[str(repo["node"]["id"].replace("/", "@"))]
                    except:
                        doc = repoCollection.createDocument()
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
                    doc["id"] = repo["node"]["id"].replace("/", "@")
                    doc["org"] = org
                    doc._key = repo["node"]["id"].replace("/", "@")
                    doc.save()
                except Exception as exception_type:
                    handling_except(type(exception_type))
            cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
        except Exception:
            cursor = False
            first = False


# DEV ###############################


def dev(db, org):
    devCollection = db['Dev']
    with open("queries/devQuery.txt", "r") as query:
        query = query.read()
    first = True
    cursor = None
    while cursor or first:
        try:
            prox = pagination_universal(query, number_of_repo=30, next=cursor, org=org)
            print(prox)
            proxRepositorios = prox["data"]["organization"]["members"]["edges"]
            for dev in proxRepositorios:
                try:
                    try:
                        doc = devCollection[str(dev["node"]["id"].replace("/", "@"))]
                    except Exception:
                        doc = devCollection.createDocument()
                    doc['devName'] = dev["node"]["name"]
                    doc["followers"] = dev["node"]["followers"]["totalCount"]
                    doc["following"] = dev["node"]["following"]["totalCount"]
                    doc["login"] = dev["node"]["login"]
                    doc["avatarUrl"] = dev["node"]["avatarUrl"]
                    doc["contributedRepositories"] = dev["node"]["contributedRepositories"]["totalCount"]
                    doc["pullRequests"] = dev["node"]["pullRequests"]["totalCount"]
                    doc["id"] = dev["node"]["id"].replace("/", "@")
                    doc["org"] = org
                    doc._key = dev["node"]["id"].replace("/", "@")
                    doc.save()
                except Exception as exception_type:
                    handling_except(type(exception_type))
            cursor = proxRepositorios[len(proxRepositorios) - 1]["cursor"]
        except Exception:
            cursor = False
            first = False


# TEAMS ###############################


def teams(db, org):
    TeamsCollection = db["Teams"]
    TeamsDevCollection = db["TeamsDev"]
    TeamsRepoCollection = db["TeamsRepo"]
    with open("queries/teamsQuery.txt", "r") as query:
        query = query.read()
    cursor = None
    hasNextPage = True
    while hasNextPage:
        try:
            prox = pagination_universal(query, number_of_repo=number_of_repos, next=cursor, org=org)
            print(prox)
            cursor = find('endCursor', prox)
            hasNextPage = find('hasNextPage', prox)
            print(hasNextPage)
            proxrepositorios = prox["data"]["organization"]["teams"]["edges"]
            for team in proxrepositorios:
                member = team["node"]["members"]
                repos = team["node"]["repositories"]
                try:
                    doc = TeamsCollection[str(team["node"]["id"].replace("/", "@"))]
                except Exception:
                    doc = TeamsCollection.createDocument()
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
                except Exception as exception_type:
                    handling_except(type(exception_type))
                try:
                    temp = db['Dev'][str(find('memberId', member)).replace("/", "@")]
                    temp2 = db['Teams'][str(team["node"]["id"]).replace("/", "@")]
                    doc = TeamsDevCollection.createEdge()
                    doc._key = (str(team["node"]["id"]) + str(find('memberId', member))).replace("/", "@")
                    doc.links(temp, temp2)
                    doc.save()
                except Exception as exception_type:
                    handling_except(type(exception_type))
                try:
                    temp = db['Repo'][str(find('repoId', repos)).replace("/", "@")]
                    temp2 = db['Teams'][str(team["node"]["id"]).replace("/", "@")]
                    doc = TeamsRepoCollection.createEdge()
                    doc._key = (str(team["node"]["id"]) + str(find('repoId', repos))).replace("/", "@")
                    doc.links(temp, temp2)
                    doc.save()
                except Exception as exception_type:
                    handling_except(type(exception_type))
        except Exception:
            cursor = None


# LANGUAGES ###############################


def languages(db, org):
    LanguagesCollection = db["Languages"]
    LanguagesRepoCollection = db["LanguagesRepo"]
    with open("queries/languagesArango.txt", "r") as aql:
        aql = aql.read()
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bindVars)

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
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next=cursor, next2=repos,
                                                org=org)
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
                        except Exception as exception_type:
                            handling_except(type(exception_type))
                        try:
                            temp = db['Languages'][str(node["node"]["id"]).replace("/", "@")]
                            temp2 = db['Repo'][str(find('repositoryId', prox)).replace("/", "@")]
                            doc = LanguagesRepoCollection.createEdge(
                                {"size": round(((node['size'] / find('totalSize', prox)) * 100), 2)})
                            doc._key = (str(node["node"]["id"]) + str(find('repositoryId', prox))).replace("/", "@")
                            doc.links(temp, temp2)
                            doc.save()
                        except Exception as exception_type:
                            handling_except(type(exception_type))
                except Exception:
                    cursor = False
                    first = False

    repositories_queue = Queue(queue_max_size)
    workers = [Thread(target=collector, args=(repositories_queue,)) for _ in range(num_of_threads)]
    for repository in queryResult:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.join() for t in workers]

# COMMITS ###############################

def commit_collector(db, org):
    commitCollection = db["Commit"]
    DevCommitCollection = db["DevCommit"]
    RepoCommitCollection = db["RepoCommit"]
    RepoDevCollection = db["RepoDev"]
    with open("queries/commitArango.txt", "r") as aql:
        aql = aql.read()
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bindVars)

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
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next=cursor, next2=repository,
                                                org=org, since=since_time, until=until_time)
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
                    doc = commitCollection[str(c["commitId"].replace("/", "@"))]
                except Exception:
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
                doc["org"] = c["org"]
                doc._key = c["commitId"].replace("/", "@")
                doc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))
            try:
                temp = db['Commit'][str(c["commitId"])]
                temp2 = db['Dev'][str(c["devId"])]
                commitDoc = DevCommitCollection.createEdge()
                commitDoc["_key"] = (str(c["commitId"]) + str(c["devId"])).replace("/", "@")
                commitDoc.links(temp2, temp)
                commitDoc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))
            try:
                temp = db['Commit'][str(c["commitId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                RepoDoc = RepoCommitCollection.createEdge()
                RepoDoc["_key"] = (str(c["commitId"]) + str(c["repositoryId"])).replace("/", "@")
                RepoDoc.links(temp2, temp)
                RepoDoc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))
            try:
                temp = db['Dev'][str(c["devId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                DevDoc = RepoDevCollection.createEdge()
                DevDoc["_key"] = (str(c["repositoryId"]) + str(c["devId"])).replace("/", "@")
                DevDoc.links(temp2, temp)
                DevDoc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    for repo in queryResult:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# README ###############################

def readme(db, org):
    with open("queries/readmeArango.txt", "r") as aql:
        aql = aql.read()
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bindVars)

    def collector(repositories: Queue, output: Queue):
        while True:
            repos = repositories.get_nowait()
            with open("queries/readmeQuery.txt", "r") as query:
                query = query.read()
            try:
                prox = pagination_universal(query, next=repos['repoName'], org=org)
                print(prox)
                output.put(1)
                if prox.get('errors'):
                    doc = db['Repo'][str(repos['key'])]
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
            except Exception as exception_type:
                handling_except(type(exception_type))

    count_queue = Queue(queue_max_size)
    repositories_queue = Queue(queue_max_size)
    workers = [Thread(target=collector, args=(repositories_queue, count_queue)) for _ in range(num_of_threads)]
    for repository in queryResult:
        repositories_queue.put(repository)
    [t.start() for t in workers]
    [t.join() for t in workers]


# STATS ###############################

def stats_collector(db, org):
    commitCollection = db["Commit"]
    with open("queries/statsQuery.txt", "r") as aql:
        aql = aql.read()
    bindVars = {"org": org, "since_time": since_time, "until_time": until_time}
    queryResult = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bindVars)

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
                doc = commitCollection[str(c["commitId"].replace("/", "@"))]
                doc['totalAddDel'] = c['totalAddDel']
                doc['additions'] = c['additions']
                doc['deletions'] = c['deletions']
                doc['numFiles'] = c['numFiles']
                doc._key = c["commitId"].replace("/", "@")
                doc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]

    for repo in queryResult:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# FORK ###############################


def fork_collector(db, org):
    ForkCollection = db["Fork"]
    DevForkCollection = db["DevFork"]
    RepoForkCollection = db["RepoFork"]
    with open("queries/forkArango.txt", "r") as aql:
        aql = aql.read()
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bindVars)

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
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next=cursor, next2=repository,
                                                org=org)
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
                    doc = ForkCollection[str(c["forkId"].replace("/", "@"))]
                except Exception:
                    doc = ForkCollection.createDocument()
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
            except Exception as exception_type:
                handling_except(type(exception_type))
            try:
                temp = db['Fork'][str(c["forkId"])]
                temp2 = db['Dev'][str(c["devId"])]
                commitDoc = DevForkCollection.createEdge()
                commitDoc["_key"] = (str(c["forkId"]) + str(c["devId"])).replace("/", "@")
                commitDoc.links(temp2, temp)
                commitDoc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))
            try:
                temp = db['Fork'][str(c["forkId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                RepoDoc = RepoForkCollection.createEdge()
                RepoDoc["_key"] = (str(c["forkId"]) + str(c["repositoryId"])).replace("/", "@")
                RepoDoc.links(temp2, temp)
                RepoDoc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    for repo in queryResult:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]


# ISSUES ###############################


def issue(db, org):
    IssueCollection = db["Issue"]
    RepoIssueCollection = db["RepoIssue"]
    with open("queries/issueArango.txt", "r") as aql:
        aql = aql.read()
    bindVars = {"org": org}
    queryResult = db.AQLQuery(aql, batchSize=batch_size, rawResults=True, bindVars=bindVars)

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
                    prox = pagination_universal(query, number_of_repo=number_of_repos, next=cursor, next2=repository,
                                                org=org)
                    print(prox)
                    if prox.get("documentation_url"):
                        print("ERROR")
                    cursor = find('endCursor', prox)
                    prox_node = find('repository', prox)
                    issues = find('edges', prox_node)
                    repository_id = prox_node["repositoryId"]
                    repo_name = prox_node["repoName"]

                    for c in issues:
                        node = c["node"]
                        author = find('author', node)
                        commit = {
                            "repositoryId": repository_id,
                            "repoName": repo_name,
                            "state": find('state', c),
                            "closedAt": find('closedAt', c),
                            "issueId": find('issueId', c),
                            "createdAt": find('createdAt', c),
                            "closed": find('closed', c),
                            "label": find('label', c),
                            "title": find('title', c),
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
                    doc = IssueCollection[str(c["issueId"].replace("/", "@"))]
                except Exception:
                    doc = IssueCollection.createDocument()
                doc["repositoryId"] = c["repositoryId"]
                doc["repoName"] = c["repoName"]
                doc["state"] = c["state"]
                doc["closedAt"] = c["closedAt"]
                doc["issueId"] = c["issueId"]
                doc["createdAt"] = c["createdAt"]
                doc["closed"] = c["closed"]
                doc["label"] = c["label"]
                doc["title"] = c["title"]
                doc["org"] = c["org"]
                doc._key = c["issueId"].replace("/", "@")
                doc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))
            try:
                temp = db['Issue'][str(c["issueId"])]
                temp2 = db['Repo'][str(c["repositoryId"])]
                RepoDoc = RepoIssueCollection.createEdge()
                RepoDoc["_key"] = (str(c["issueId"]) + str(c["repositoryId"])).replace("/", "@")
                RepoDoc.links(temp2, temp)
                RepoDoc.save()
            except Exception as exception_type:
                handling_except(type(exception_type))

    repositories_queue = Queue(queue_max_size)
    commits_queue = Queue(queue_max_size)

    workers = [Thread(target=collector, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    workers2 = [Thread(target=save, args=(repositories_queue, commits_queue)) for _ in range(num_of_threads)]
    for repo in queryResult:
        repositories_queue.put(repo)
    [t.start() for t in workers]
    [t.start() for t in workers2]
    [t.join() for t in workers]
    [t.join() for t in workers2]
