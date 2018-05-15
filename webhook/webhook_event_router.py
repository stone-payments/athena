import pprint
from threading import Thread

from collection_modules.module import find_key
from webhook.webhook_delete_branch import DeleteBranch
from webhook.webhook_dev_event import GetDevEvent
from webhook.webhook_get_commit import GetCommit
from webhook.webhook_issues_event import GetIssueEvent
from webhook.webhook_new_branch import GetBranch
from webhook.webhook_repository_event import GetRepositoryEvent
from webhook.webhook_team_event import GetTeamEvent


class WebhookEventRouter:

    def __init__(self, db, webhook_queue):
        self.webhook_queue = webhook_queue
        self.db = db

    @staticmethod
    def __parse_branch_string(data):
        return '/'.join(data.split("/")[:2])

    def webhook_event_router(self):
        while True:
            returned_data = self.webhook_queue.get(block=True)
            # returned_data = issues()
            event = returned_data[0]
            data = returned_data[1]
            if event == 'push' and not find_key("deleted", data) and not find_key("forced", data) and \
                    not find_key("base_ref", data) and self.__parse_branch_string(find_key("ref", data)) == "refs/heads":
                print("NEW COMMIT")
                # pprint.pprint(data)
                GetCommit(self.db).get_data(data)
            elif event == 'push' and find_key("created", data) and not find_key("deleted", data) \
                    and not find_key("forced", data) and find_key("base_ref", data):
                print("NEW BRANCH")
                # pprint.pprint(data)
                GetBranch(self.db).get_data(data)
            elif event == 'delete' and find_key('ref_type', data) == "branch":
                print("DELETE")
                # pprint.pprint(data)
                DeleteBranch(self.db).get_data(data)
            elif event == "repository":
                print("repository")
                # pprint.pprint(data)
                GetRepositoryEvent(self.db).get_data(data)
            elif event == "organization":
                print("organization")
                # pprint.pprint(data)
                GetDevEvent(self.db).get_data(data)
            elif event == "team":
                print("team")
                # pprint.pprint(data)
                GetTeamEvent(self.db).get_data(data)
            elif event == "membership":
                print("membership")
                # pprint.pprint(data)
                GetTeamEvent(self.db).get_member_data(data)
            elif event == "issues":
                print("issues")
                pprint.pprint(data)
                GetIssueEvent(self.db).get_data(data)

    def start(self):
        workers = [Thread(target=self.webhook_event_router, args=()) for _ in range(1)]
        [t.start() for t in workers]
