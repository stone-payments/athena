from collection_modules.module import find_key
import datetime
from datetime import date
from collections_edges import Commit
from app import db
from webhook_graphql_queries.webhook_graphql_queries import webhook_commits_query
import pprint



teste = {'after': '7f7764f7a224197b158713259c4e296e76e28299',
 'base_ref': None,
 'before': 'a4750481bc6154e311ff128c93f419d145762b21',
 'commits': [{'added': [],
              'author': {'email': 'mralves@stone.com.br',
                         'name': 'mralves',
                         'username': 'mralves'},
              'committer': {'email': 'mralves@stone.com.br',
                            'name': 'mralves',
                            'username': 'mralves'},
              'distinct': True,
              'id': '7f7764f7a224197b158713259c4e296e76e28299',
              'message': 'fix: decrease timeout of sockets tcp',
              'modified': ['src/main/resources/application.conf'],
              'removed': [],
              'timestamp': '2018-03-26T17:16:17-03:00',
              'tree_id': '0b5ef7366d0e16854bf576d04a4aa546c3cad267',
              'url': 'https://github.com/stone-payments/transaction-scout/commit/7f7764f7a224197b158713259c4e296e76e28299'}],
 'compare': 'https://github.com/stone-payments/transaction-scout/compare/a4750481bc61...7f7764f7a224',
 'created': False,
 'deleted': False,
 'forced': False,
 'head_commit': {'added': [],
                 'author': {'email': 'mralves@stone.com.br',
                            'name': 'mralves',
                            'username': 'mralves'},
                 'committer': {'email': 'mralves@stone.com.br',
                               'name': 'mralves',
                               'username': 'mralves'},
                 'distinct': True,
                 'id': '7f7764f7a224197b158713259c4e296e76e28299',
                 'message': 'fix: decrease timeout of sockets tcp',
                 'modified': ['src/main/resources/application.conf'],
                 'removed': [],
                 'timestamp': '2018-03-26T17:16:17-03:00',
                 'tree_id': '0b5ef7366d0e16854bf576d04a4aa546c3cad267',
                 'url': 'https://github.com/stone-payments/transaction-scout/commit/7f7764f7a224197b158713259c4e296e76e28299'},
 'organization': {'avatar_url': 'https://avatars1.githubusercontent.com/u/8750624?v=4',
                  'description': 'Pensar fora da máquina só é possível quando '
                                 'se trabalha com tecnologia humana de ponta.',
                  'events_url': 'https://api.github.com/orgs/stone-payments/events',
                  'hooks_url': 'https://api.github.com/orgs/stone-payments/hooks',
                  'id': 8750624,
                  'issues_url': 'https://api.github.com/orgs/stone-payments/issues',
                  'login': 'stone-payments',
                  'members_url': 'https://api.github.com/orgs/stone-payments/members{/member}',
                  'public_members_url': 'https://api.github.com/orgs/stone-payments/public_members{/member}',
                  'repos_url': 'https://api.github.com/orgs/stone-payments/repos',
                  'url': 'https://api.github.com/orgs/stone-payments'},
 'pusher': {'email': 'mateusra@id.uff.br', 'name': 'mralves'},
 'ref': 'refs/heads/tcp-leak',
 'repository': {'archive_url': 'https://api.github.com/repos/stone-payments/transaction-scout/{archive_format}{/ref}',
                'archived': False,
                'assignees_url': 'https://api.github.com/repos/stone-payments/transaction-scout/assignees{/user}',
                'blobs_url': 'https://api.github.com/repos/stone-payments/transaction-scout/git/blobs{/sha}',
                'branches_url': 'https://api.github.com/repos/stone-payments/transaction-scout/branches{/branch}',
                'clone_url': 'https://github.com/stone-payments/transaction-scout.git',
                'collaborators_url': 'https://api.github.com/repos/stone-payments/transaction-scout/collaborators{/collaborator}',
                'comments_url': 'https://api.github.com/repos/stone-payments/transaction-scout/comments{/number}',
                'commits_url': 'https://api.github.com/repos/stone-payments/transaction-scout/commits{/sha}',
                'compare_url': 'https://api.github.com/repos/stone-payments/transaction-scout/compare/{base}...{head}',
                'contents_url': 'https://api.github.com/repos/stone-payments/transaction-scout/contents/{+path}',
                'contributors_url': 'https://api.github.com/repos/stone-payments/transaction-scout/contributors',
                'created_at': 1499171625,
                'default_branch': 'develop',
                'deployments_url': 'https://api.github.com/repos/stone-payments/transaction-scout/deployments',
                'description': None,
                'downloads_url': 'https://api.github.com/repos/stone-payments/transaction-scout/downloads',
                'events_url': 'https://api.github.com/repos/stone-payments/transaction-scout/events',
                'fork': False,
                'forks': 0,
                'forks_count': 0,
                'forks_url': 'https://api.github.com/repos/stone-payments/transaction-scout/forks',
                'full_name': 'stone-payments/transaction-scout',
                'git_commits_url': 'https://api.github.com/repos/stone-payments/transaction-scout/git/commits{/sha}',
                'git_refs_url': 'https://api.github.com/repos/stone-payments/transaction-scout/git/refs{/sha}',
                'git_tags_url': 'https://api.github.com/repos/stone-payments/transaction-scout/git/tags{/sha}',
                'git_url': 'git://github.com/stone-payments/transaction-scout.git',
                'has_downloads': True,
                'has_issues': False,
                'has_pages': False,
                'has_projects': False,
                'has_wiki': False,
                'homepage': None,
                'hooks_url': 'https://api.github.com/repos/stone-payments/transaction-scout/hooks',
                'html_url': 'https://github.com/stone-payments/transaction-scout',
                'id': 96216314,
                'issue_comment_url': 'https://api.github.com/repos/stone-payments/transaction-scout/issues/comments{/number}',
                'issue_events_url': 'https://api.github.com/repos/stone-payments/transaction-scout/issues/events{/number}',
                'issues_url': 'https://api.github.com/repos/stone-payments/transaction-scout/issues{/number}',
                'keys_url': 'https://api.github.com/repos/stone-payments/transaction-scout/keys{/key_id}',
                'labels_url': 'https://api.github.com/repos/stone-payments/transaction-scout/labels{/name}',
                'language': 'Kotlin',
                'languages_url': 'https://api.github.com/repos/stone-payments/transaction-scout/languages',
                'license': {'key': 'gpl-3.0',
                            'name': 'GNU General Public License v3.0',
                            'spdx_id': 'GPL-3.0',
                            'url': 'https://api.github.com/licenses/gpl-3.0'},
                'master_branch': 'develop',
                'merges_url': 'https://api.github.com/repos/stone-payments/transaction-scout/merges',
                'milestones_url': 'https://api.github.com/repos/stone-payments/transaction-scout/milestones{/number}',
                'mirror_url': None,
                'name': 'transaction-scout',
                'notifications_url': 'https://api.github.com/repos/stone-payments/transaction-scout/notifications{?since,all,participating}',
                'open_issues': 2,
                'open_issues_count': 2,
                'organization': 'stone-payments',
                'owner': {'avatar_url': 'https://avatars1.githubusercontent.com/u/8750624?v=4',
                          'email': 'opensource@stone.com.br',
                          'events_url': 'https://api.github.com/users/stone-payments/events{/privacy}',
                          'followers_url': 'https://api.github.com/users/stone-payments/followers',
                          'following_url': 'https://api.github.com/users/stone-payments/following{/other_user}',
                          'gists_url': 'https://api.github.com/users/stone-payments/gists{/gist_id}',
                          'gravatar_id': '',
                          'html_url': 'https://github.com/stone-payments',
                          'id': 8750624,
                          'login': 'stone-payments',
                          'name': 'stone-payments',
                          'organizations_url': 'https://api.github.com/users/stone-payments/orgs',
                          'received_events_url': 'https://api.github.com/users/stone-payments/received_events',
                          'repos_url': 'https://api.github.com/users/stone-payments/repos',
                          'site_admin': False,
                          'starred_url': 'https://api.github.com/users/stone-payments/starred{/owner}{/repo}',
                          'subscriptions_url': 'https://api.github.com/users/stone-payments/subscriptions',
                          'type': 'Organization',
                          'url': 'https://api.github.com/users/stone-payments'},
                'private': True,
                'pulls_url': 'https://api.github.com/repos/stone-payments/transaction-scout/pulls{/number}',
                'pushed_at': 1522095382,
                'releases_url': 'https://api.github.com/repos/stone-payments/transaction-scout/releases{/id}',
                'size': 355,
                'ssh_url': 'git@github.com:stone-payments/transaction-scout.git',
                'stargazers': 1,
                'stargazers_count': 1,
                'stargazers_url': 'https://api.github.com/repos/stone-payments/transaction-scout/stargazers',
                'statuses_url': 'https://api.github.com/repos/stone-payments/transaction-scout/statuses/{sha}',
                'subscribers_url': 'https://api.github.com/repos/stone-payments/transaction-scout/subscribers',
                'subscription_url': 'https://api.github.com/repos/stone-payments/transaction-scout/subscription',
                'svn_url': 'https://github.com/stone-payments/transaction-scout',
                'tags_url': 'https://api.github.com/repos/stone-payments/transaction-scout/tags',
                'teams_url': 'https://api.github.com/repos/stone-payments/transaction-scout/teams',
                'trees_url': 'https://api.github.com/repos/stone-payments/transaction-scout/git/trees{/sha}',
                'updated_at': '2018-03-22T12:19:50Z',
                'url': 'https://github.com/stone-payments/transaction-scout',
                'watchers': 1,
                'watchers_count': 1},
 'sender': {'avatar_url': 'https://avatars3.githubusercontent.com/u/10778459?v=4',
            'events_url': 'https://api.github.com/users/mralves/events{/privacy}',
            'followers_url': 'https://api.github.com/users/mralves/followers',
            'following_url': 'https://api.github.com/users/mralves/following{/other_user}',
            'gists_url': 'https://api.github.com/users/mralves/gists{/gist_id}',
            'gravatar_id': '',
            'html_url': 'https://github.com/mralves',
            'id': 10778459,
            'login': 'mralves',
            'organizations_url': 'https://api.github.com/users/mralves/orgs',
            'received_events_url': 'https://api.github.com/users/mralves/received_events',
            'repos_url': 'https://api.github.com/users/mralves/repos',
            'site_admin': False,
            'starred_url': 'https://api.github.com/users/mralves/starred{/owner}{/repo}',
            'subscriptions_url': 'https://api.github.com/users/mralves/subscriptions',
            'type': 'User',
            'url': 'https://api.github.com/users/mralves'}}


class GetCommit:

    @staticmethod
    def __parse_date(date):
        if date is None:
            return None
        timezone = date[-6:-3]
        date = date[:-6]
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        return (date + datetime.timedelta(hours=-int(timezone))).strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def __parse_branch(data):
        return data[11:]

    def get_data(self, raw_json):
        repo_name = find_key('repository', raw_json)
        repo_name = find_key('name', repo_name)
        commit_list = find_key('commits', raw_json)
        since_timestamp = self.__parse_date(find_key('timestamp', commit_list[0]))
        until_timestamp = self.__parse_date(find_key('timestamp', commit_list[-1]))
        if not since_timestamp or not until_timestamp:
            head_commit = find_key('head_commit', raw_json)
            since_timestamp = until_timestamp = self.__parse_date(find_key('timestamp', head_commit))
        branch = self.__parse_branch(find_key('ref', raw_json))
        commit = Commit(db, "stone-payments", webhook_commits_query, collection_name="Commit", branch_name=branch,
                        since_commit=since_timestamp, until_commit=until_timestamp, repo_name=repo_name)
        commit.collect_webhook()




