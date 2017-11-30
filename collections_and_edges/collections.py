from collector import *
from validators import *


# REPO ###############################

def org_collection(db, org, query, collection_name, edge_name="edges"):
    def content(self, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find('id', node)),
            "avatarUrl": string_validate(find('avatarUrl', node)),
            "description": string_validate(find('description', node)),
            "membersCount": int_validate(find('membersCount', node)),
            "teamsCount": int_validate(find('teamsCount', node)),
            "repoCount": int_validate(find('repoCount', node)),
            "projectCount": int_validate(find('projectCount', node)),
            "db_last_updated": datetime.datetime.utcnow(),
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


def repo(db, org, query, collection_name, edge_name="edges"):
    def content(self, response, node):
        readme_ranges = find('ranges', node)
        if readme_ranges:
            readme = "OK" if readme_ranges[-1]['endingLine'] >= 5 else "Poor"
        else:
            readme = None
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(node["node"]["repoId"].replace("/", "@")),
            "repoName": string_validate(node["node"]["name"], not_none=True),
            "description": string_validate(node["node"]["description"]),
            "url": string_validate(node["node"]["url"]),
            "openSource": bool_validate(False if node["node"]["isPrivate"] else True),
            "primaryLanguage": string_validate(find('priLanguage', node)),
            "forks": int_validate(node["node"]["forks"]["totalCount"]),
            "issues": int_validate(node["node"]["issues"]["totalCount"]),
            "stargazers": int_validate(node["node"]["stargazers"]["totalCount"]),
            "watchers": int_validate(node["node"]["watchers"]["totalCount"]),
            "createdAt": convert_datetime(find('createdAt', node)),
            "nameWithOwner": string_validate(node["node"]["nameWithOwner"]),
            "licenseId": string_validate(find('licenseId', node)),
            "licenseType": string_validate(find('licenseType', node)),
            "readme": string_validate(readme),
            "db_last_updated": datetime.datetime.utcnow(),
            "languages": parse_multiple_languages(node, "language_edges", "languageName",
                                                  "languageSize"),
            "committed_today": bool_validate(False if find('committedDate', node) is None else True)
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


def dev(db, org, query, collection_name, edge_name="edges"):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find("id", node)),
            "devName": string_validate(find("name", node)),
            "followers": int_validate(node["node"]["followers"]["totalCount"]),
            "following": int_validate(node["node"]["following"]["totalCount"]),
            "login": string_validate(node["node"]["login"], not_none=True),
            "avatarUrl": string_validate(node["node"]["avatarUrl"]),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node, response):
        save_edges = [
        ]
        return save_edges

    start = Collector(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                      number_of_repo=number_of_repos, since=since_time, until=until_time,
                      save_content=content, save_edges=edges)
    start.start()


# TEAMS ###############################


def teams(db, org, query, collection_name, edge_name="edges"):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find('teamId', node)),
            'createdAt': convert_datetime(find('createdAt', node)),
            "teamName": string_validate(node["node"]["name"], not_none=True),
            "privacy": string_validate(node["node"]["privacy"]),
            "slug": string_validate(node["node"]["slug"], not_none=True),
            "membersCount": int_validate(find('membersCount', node)),
            "repoCount": int_validate(find('repoCount', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(team, members, repos):
        collect_member_of_team = [
            {
                "edge_name": "dev_to_team",
                'to': find('_id', team),
                'from': find('memberId', member),
                "db_last_updated": datetime.datetime.utcnow(),
            }
            for member in members
        ]
        collect_repositories_of_team = [
            {
                "edge_name": "repo_to_team",
                'to': find('_id', team),
                'from': find('repoId', repo_slice),
                "db_last_updated": datetime.datetime.utcnow(),
            }
            for repo_slice in repos
        ]
        return collect_member_of_team, collect_repositories_of_team

    start = Collector(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                      number_of_repo=number_of_repos, since=since_time, until=until_time,
                      save_content=content, save_edges=edges)
    start.start_team()


# TEAMS_DEV ###############################

def teams_dev(db, org, query, query_db, edges_name="edges"):
    def content(self, response, node):
        save_content = {
        }
        return save_content

    def edges(response, node):
        save_edges = [{
            "edge_name": "dev_to_team",
            'to': find('teamId', response),
            'from': find('memberId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        ]
        return save_edges

    start = CollectorThread(db=db, org=org, edges=edges_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(team_dev=True)


# TEAMS_REPO ###############################

def teams_repo(db, org, query, query_db, edges_name="edges"):
    def content(self, response, node):
        save_content = {
        }
        return save_content

    def edges(response, node):
        save_edges = [{
            "edge_name": "dev_to_repo",
            'to': find('teamId', response),
            'from': find('repoId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        ]
        return save_edges

    start = CollectorThread(db=db, org=org, edges=edges_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(team_dev=True)


# COMMITS ###############################

def commit_collector(db, org, query, query_db, collection_name, edge_name="edges"):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find('commitId', node)),
            "repositoryId": string_validate(find('repositoryId', response), not_none=True),
            "repoName": string_validate(find('repoName', response), not_none=True),
            "branchName": string_validate(find('branchName', response)),
            "messageHeadline": string_validate(find('messageHeadline', node)),
            "oid": not_null(find('oid', node)),
            # "committedDate": string_validate(find('committedDate', node), not_none=True),
            "committedDate": convert_datetime(find('committedDate', node)),
            "author": string_validate(find('login', node)),
            "devId": string_validate(find('devId', node)),
            "commitId": string_validate(find('commitId', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "commit_dev",
            "to": find('commitId', node),
            "from": find('devId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        },
            {
                "edge_name": "commit_repo",
                "to": find('commitId', node),
                "from": find('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            },
            {
                "edge_name": "dev_repo",
                "to": find('devId', node),
                "from": find('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                            since=since_time, until=until_time, query_db=query_db, number_of_repo=number_of_repos,
                            save_content=content, save_edges=edges)
    start.start()


# STATS ###############################

def stats_collector(db, org, query, stats_query, collection_name, edge_name="edges"):
    def content(node, commit_id):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "_id": not_null(commit_id),
            'totalAddDel': int_validate(node['stats']['total']),
            'additions': int_validate(node['stats']['additions']),
            'deletions': int_validate(node['stats']['deletions']),
            'numFiles': int_validate(len(node['files']))
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

def fork_collector(db, org, query, query_db, collection_name, edge_name="edges"):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find('forkId', node)),
            "repositoryId": not_null(find('repositoryId', response)),
            "repoName": string_validate(find('repoName', response)),
            "createdAt": convert_datetime(find('createdAt', node)),
            "isPrivate": bool_validate(find('isPrivate', node)),
            "isLocked": bool_validate(find('isLocked', node)),
            "devId": string_validate(find('devId', node)),
            "login": string_validate(find('login', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "fork_to_dev",
            "to": find('_id', node),
            "from": find('devId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        },
            {
                "edge_name": "fork_to_repo",
                "to": find('_id', node),
                "from": find('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start()


# ISSUES ###############################

def issue(db, org, query, query_db, collection_name, edge_name="edges"):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find('issueId', node)),
            "repositoryId": not_null(find('repositoryId', response)),
            "repoName": string_validate(find('repoName', response)),
            "state": string_validate(find('state', node)),
            "closed_login": string_validate(find('closed_login', node)),
            "closedAt": convert_datetime(find('closedAt', node)),
            "created_login": string_validate(find('created_login', node)),
            "createdAt": convert_datetime(find('createdAt', node)),
            "authorAssociation": string_validate(find('authorAssociation', node)),
            "closed": bool_validate(find('closed', node)),
            "label": string_validate(find('label', node)),
            "title": string_validate(find('title', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [
            {
                "edge_name": "issue_to_repo",
                "to": find('_id', node),
                "from": find('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    start = CollectorThread(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                            query_db=query_db, number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start()
