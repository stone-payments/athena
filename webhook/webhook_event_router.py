from collection_modules.module import find_key
from webhook.webhook_get_commit import GetCommit
from webhook.webhook_new_branch import GetBranch
from webhook.webhook_delete_branch import DeleteBranch
from webhook.webhook_new_repository import GetNewRepository
from threading import Thread
import pprint
from app import db


class WebhookEventRouter:

    def __init__(self, webhook_queue):
        self.webhook_queue = webhook_queue

    @staticmethod
    def __parse_branch_string(data):
        return '/'.join(data.split("/")[:2])

    def webhook_event_router(self):
        while True:
            returned_data = self.webhook_queue.get(block=True)
            event = returned_data[0]
            data = returned_data[1]
            if event == 'push' and not find_key("deleted", data) and not find_key("forced", data) and \
                    not find_key("base_ref", data) and self.__parse_branch_string(find_key("ref", data)) == "refs/heads":
                print("NEW COMMIT")
                pprint.pprint(data)
                get_commit = GetCommit(db)
                get_commit.get_data(data)
            elif event == 'push' and find_key("created", data) and not find_key("deleted", data) \
                    and not find_key("forced", data) and find_key("base_ref", data):
                print("NEW BRANCH")
                pprint.pprint(data)
                get_new_branch = GetBranch(db)
                get_new_branch.get_data(data)
            elif event == 'delete' and find_key('ref_type', data) == "branch":
                print("DELETE")
                pprint.pprint(data)
                delete_branch = DeleteBranch(db)
                delete_branch.get_data(data)
            elif event == 'create' and find_key('ref_type', data) == "repository":
                print("create")
                pprint.pprint(data)
                new_repository = GetNewRepository(db)
                new_repository.get_data(data)

    def start(self):
        workers = [Thread(target=self.webhook_event_router, args=()) for _ in range(1)]
        [t.start() for t in workers]
