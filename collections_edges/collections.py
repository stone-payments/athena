from collector import *
from validators import *
import datetime


# REPO ###############################

def org_collection(db, org, query, collection_name, edge_name="edges"):
    def content(self, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('id', node)),
            "avatarUrl": string_validate(find_key('avatarUrl', node)),
            "description": string_validate(find_key('description', node)),
            "membersCount": int_validate(find_key('membersCount', node)),
            "teamsCount": int_validate(find_key('teamsCount', node)),
            "repoCount": int_validate(find_key('repoCount', node)),
            "projectCount": int_validate(find_key('projectCount', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(*_):
        save_edges = [
        ]
        return save_edges

    start = CollectorGeneric(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                             number_of_repo=repo_number_of_repos, updated_utc_time=utc_time,
                             save_content=content, save_edges=edges)
    start.start()


def repo(db, org, query, collection_name, edge_name="edges"):
    def content(self, _, node):
        readme_ranges = find_key('ranges', node)
        if readme_ranges:
            readme = "OK" if readme_ranges[-1]['endingLine'] >= 5 else "Poor"
        else:
            readme = None
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": node["node"]["repoId"],
            "repoName": string_validate(node["node"]["name"], not_none=True),
            "description": string_validate(node["node"]["description"]),
            "url": string_validate(node["node"]["url"]),
            "openSource": bool_validate(False if node["node"]["isPrivate"] else True),
            "primaryLanguage": string_validate(find_key('priLanguage', node)),
            "forks": int_validate(node["node"]["forks"]["totalCount"]),
            "issues": int_validate(node["node"]["issues"]["totalCount"]),
            "stargazers": int_validate(node["node"]["stargazers"]["totalCount"]),
            "watchers": int_validate(node["node"]["watchers"]["totalCount"]),
            "createdAt": convert_datetime(find_key('createdAt', node)),
            "nameWithOwner": string_validate(node["node"]["nameWithOwner"]),
            "licenseId": string_validate(find_key('licenseId', node)),
            "licenseType": string_validate(find_key('licenseType', node)),
            "readme": string_validate(readme),
            "db_last_updated": datetime.datetime.utcnow(),
            "languages": parse_multiple_languages(node, "language_edges", "languageName",
                                                  "languageSize"),
            "committed_today": bool_validate(False if find_key('committedInRangeDate', node) is None else True)
        }
        return save_content

    def edges(*_):
        save_edges = [
        ]
        return save_edges

    start = CollectorGeneric(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                             number_of_repo=repo_number_of_repos, updated_utc_time=utc_time,
                             save_content=content, save_edges=edges)
    start.start()


# DEV ###############################


def dev(db, org, query, collection_name, edge_name="edges"):
    def content(self, _, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": find_key("id", node),
            "devName": string_validate(find_key("name", node)),
            "followers": int_validate(node["node"]["followers"]["totalCount"]),
            "following": int_validate(node["node"]["following"]["totalCount"]),
            "login": string_validate(node["node"]["login"], not_none=True),
            "avatarUrl": string_validate(node["node"]["avatarUrl"]),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(*_):
        save_edges = [
        ]
        return save_edges

    start = CollectorGeneric(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                             number_of_repo=number_of_repos, updated_utc_time=utc_time,
                             save_content=content, save_edges=edges)
    start.start()


# TEAMS ###############################


def teams(db, org, query, collection_name, edge_name="edges"):
    def content(self, _, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": find_key('teamId', node),
            'createdAt': convert_datetime(find_key('createdAt', node)),
            "teamName": string_validate(node["node"]["name"], not_none=True),
            "privacy": string_validate(node["node"]["privacy"]),
            "slug": string_validate(node["node"]["slug"], not_none=True),
            "membersCount": int_validate(find_key('membersCount', node)),
            "repoCount": int_validate(find_key('repoCount', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(team, members, repos):
        collect_member_of_team = [
            {
                "edge_name": "dev_to_team",
                'to': find_key('_id', team),
                'from': find_key('memberId', member),
                "db_last_updated": datetime.datetime.utcnow(),
            }
            for member in members
        ]
        collect_repositories_of_team = [
            {
                "edge_name": "repo_to_team",
                'to': find_key('_id', team),
                'from': find_key('repoId', repo_slice),
                "db_last_updated": datetime.datetime.utcnow(),
            }
            for repo_slice in repos
        ]
        return collect_member_of_team, collect_repositories_of_team

    start = CollectorTeam(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                          number_of_repo=number_of_repos, updated_utc_time=utc_time,
                          save_content=content, save_edges=edges)
    start.start()


# TEAMS_DEV ###############################

def teams_dev(db, org, query, query_db, save_queue_type, edges_name="edges"):
    def content(*_):
        save_content = {
        }
        return save_content

    def edges(response, node):
        save_edges = [{
            "edge_name": "dev_to_team",
            'to': find_key('teamId', response),
            'from': find_key('memberId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        ]
        return save_edges

    start = CollectorRestrictedTeam(db=db, org=org, edges=edges_name, query=query,
                                    query_db=query_db, number_of_repo=number_of_repos, save_content=content,
                                    save_edges=edges)
    start.start(save_queue_type)


# TEAMS_REPO ###############################

def teams_repo(db, org, query, query_db, save_queue_type, edges_name="edges"):
    def content(*_):
        save_content = {
        }
        return save_content

    def edges(response, node):
        save_edges = [{
            "edge_name": "dev_to_repo",
            'to': find_key('teamId', response),
            'from': find_key('repoId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        ]
        return save_edges

    start = CollectorRestrictedTeam(db=db, org=org, edges=edges_name, query=query,
                                    query_db=query_db, number_of_repo=number_of_repos, save_content=content,
                                    save_edges=edges)
    start.start(save_queue_type)


# COMMITS ###############################

def commit_collector(db, org, query, query_db, collection_name, save_queue_type, edge_name="edges", ):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('commitId', node)),
            "repositoryId": string_validate(find_key('repositoryId', response), not_none=True),
            "repoName": string_validate(find_key('repoName', response), not_none=True),
            "branchName": string_validate(find_key('branchName', response)),
            "messageHeadline": string_validate(find_key('messageHeadline', node)),
            "oid": not_null(find_key('oid', node)),
            # "committedDate": string_validate(find('committedDate', node), not_none=True),
            "committedDate": convert_datetime(find_key('committedDate', node)),
            "author": string_validate(find_key('login', node)),
            "devId": string_validate(find_key('devId', node)),
            "commitId": string_validate(find_key('commitId', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "commit_dev",
            "to": find_key('commitId', node),
            "from": find_key('devId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        },
            {
                "edge_name": "commit_repo",
                "to": find_key('commitId', node),
                "from": find_key('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            },
            {
                "edge_name": "dev_repo",
                "to": find_key('devId', node),
                "from": find_key('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    start = CollectorRestricted(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                                updated_utc_time=utc_time, query_db=query_db,
                                number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(save_queue_type)


# STATS ###############################

def stats_collector(db, org, query, stats_query, collection_name, save_queue_type, edge_name="edges"):
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

    def edges(_):
        save_edges = [
        ]
        return save_edges

    start = CollectorStats(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                           query_db=stats_query, number_of_repo=number_of_repos, save_content=content,
                           save_edges=edges)
    start.start(save_queue_type)


# FORK ###############################

def fork_collector(db, org, query, query_db, collection_name, save_queue_type, edge_name="edges"):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('forkId', node)),
            "repositoryId": not_null(find_key('repositoryId', response)),
            "repoName": string_validate(find_key('repoName', response)),
            "createdAt": convert_datetime(find_key('createdAt', node)),
            "isPrivate": bool_validate(find_key('isPrivate', node)),
            "isLocked": bool_validate(find_key('isLocked', node)),
            "devId": string_validate(find_key('devId', node)),
            "login": string_validate(find_key('login', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [{
            "edge_name": "fork_to_dev",
            "to": find_key('_id', node),
            "from": find_key('devId', node),
            "db_last_updated": datetime.datetime.utcnow(),
        },
            {
                "edge_name": "fork_to_repo",
                "to": find_key('_id', node),
                "from": find_key('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    start = CollectorRestricted(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                                updated_utc_time=utc_time, query_db=query_db,
                                number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(save_queue_type)


# ISSUES ###############################

def issue(db, org, query, query_db, collection_name, save_queue_type, edge_name="edges", ):
    def content(self, response, node):
        save_content = {
            "collection_name": string_validate(collection_name),
            "org": string_validate(self.org, not_none=True),
            "_id": not_null(find_key('issueId', node)),
            "repositoryId": not_null(find_key('repositoryId', response)),
            "repoName": string_validate(find_key('repoName', response)),
            "state": string_validate(find_key('state', node)),
            "closed_login": string_validate(find_key('closed_login', node)),
            "closedAt": convert_datetime(find_key('closedAt', node)),
            "created_login": string_validate(find_key('created_login', node)),
            "createdAt": convert_datetime(find_key('createdAt', node)),
            "authorAssociation": string_validate(find_key('authorAssociation', node)),
            "closed": bool_validate(find_key('closed', node)),
            "label": string_validate(find_key('label', node)),
            "title": string_validate(find_key('title', node)),
            "db_last_updated": datetime.datetime.utcnow(),
        }
        return save_content

    def edges(node):
        save_edges = [
            {
                "edge_name": "issue_to_repo",
                "to": find_key('_id', node),
                "from": find_key('repositoryId', node),
                "db_last_updated": datetime.datetime.utcnow(),
            }
        ]
        return save_edges

    start = CollectorRestricted(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                                updated_utc_time=utc_time, query_db=query_db,
                                number_of_repo=number_of_repos, save_content=content, save_edges=edges)
    start.start(save_queue_type)
