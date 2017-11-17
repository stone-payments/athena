from module import *


# REPO ###############################

def repo2(db, org, query, collection_name, edge_name="edges"):

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


def dev2(db, org, query, collection_name, edge_name="edges"):

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


def teams2(db, org, query, collection_name, edge_name="edges"):

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
                "edge_name": "repo_to_team",
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


# COMMITS ###############################

def commit_collector2(db, org, query, query_db, collection_name, edge_name="edges"):
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
            "org": self.org,
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')),
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "commit_dev",
            "to": find('commitId', node),
            "from": find('devId', node),
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        },
            {
                "edge_name": "commit_repo",
                "to": find('commitId', node),
                "from": find('repositoryId', node),
                "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
            },
            {
                "edge_name": "dev_repo",
                "to": find('devId', node),
                "from": find('repositoryId', node),
                "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')),
            }
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start()


# STATS ###############################

def stats_collector2(db, org, query, stats_query, collection_name, edge_name="edges"):
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

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                            query_db=stats_query, number_of_repo=number_of_repos, save_content=content,
                            save_edges=edges)
    start.start(stats=True)


# FORK ###############################

def fork_collector2(db, org, query, query_db, collection_name, edge_name="edges"):
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
            "org": self.org,
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')),
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

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start()


# ISSUES ###############################

def issue2(db, org, query, query_db, collection_name, edge_name="edges"):
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
            "org": self.org,
            "db_last_updated": str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')),
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

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start()
