import json
from datetime import datetime


def find(key, json) -> object:
    if isinstance(json, list):
        for item in json:
            f = find(key, item)
            if f is not None:
                return f
    elif isinstance(json, dict):
        if key in json:
            return json[key]
        else:
            for inner in json.values():
                f = find(key, inner)
                if f is not None:
                    return f
    return None


def collect_repositories_of_team(team, repos):
    return [
        {
            'team_id': team,
            'repository_id': repo['node']['repoId']
        }
        for repo in repos
    ]


def collect_member_of_team(team, members):
    return [
        {
            'team_id': team,
            'member_id': member['node']['memberId']
        }
        for member in members
    ]


def edges(team, members, repos):
    collect_member_of_team = [
        {
            'team_id': team,
            'member_id': member['node']['memberId']
        }
        for member in members
    ]
    collect_repositories_of_team = [
        {
            'team_id': team,
            'repository_id': repo['node']['repoId']
        }
        for repo in repos
    ]
    return collect_member_of_team, collect_repositories_of_team


def content(self, response, node):
    save_content = {
        "collection_name": "GHEHE",
        'createdAt': find('createdAt', node),
        "teamName": find('name', node),
        "privacy": find('privacy', node),
        "slug": find('slug', node),
        "membersCount": find('membersCount', node),
        "repoCount": find('repoCount', node),
        "_id": find('teamId', node),
        "org": "stone-payments",
        "db_last_updated": str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    }
    return save_content


class TeamCollector:
    def __init__(self, repository_edge_collector, member_edge_collector, content, edges):
        self.repository_edge_collector = repository_edge_collector
        self.member_edge_collector = member_edge_collector
        self.content = content
        self.edges = edges

    def collect(self, edges):
        teams = []
        for node in edges:
            # print(item)
            # item = item['node']
            # team = {
            #     'create_at': item['createdAt'],
            #     'team_id': item['teamId'],
            #     'name': item['name'],
            #     'privacy': item['privacy'],
            #     'slug': item['slug'],
            # }
            team = self.content(self, edges, node)
            # print(team)
            # repositories = self.repository_edge_collector(team['_id'], item['repositories']['repo_edge'])
            #
            # members = self.member_edge_collector(team['_id'], item['members']['members_edge'])
            members, repositories = self.edges(team['_id'], find('members_edge', node), find('repo_edge', node))
            print(members)
            team['repositories'] = repositories
            team['members'] = members
            teams.append(team)
        return teams


inp = open('C:\\Users\\philippe.maia\\Documents\\page.json', encoding='UTF-8')
page = json.loads(inp.read())
team_collector = TeamCollector(collect_repositories_of_team, collect_member_of_team, content, edges)
teams = team_collector.collect(page)
print(teams)
