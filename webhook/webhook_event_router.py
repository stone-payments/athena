from collection_modules.module import find_key
from webhook.webhook_get_commit import GetCommit
from webhook.webhook_get_branch import GetBranch
from threading import Thread
import pprint
from app import db


class WebhookEventRouter:

    def __init__(self, webhook_queue):
        self.webhook_queue = webhook_queue

    def webhook_event_router(self):
        while True:
            returned_data = self.webhook_queue.get(block=True)
            event = returned_data[0]
            data = returned_data[1]
            if event == 'push' and not find_key("deleted", data) and not find_key("forced", data) and \
                    not find_key("base_ref", data):
                pprint.pprint(data)
                get_commit = GetCommit(db)
                get_commit.get_data(data)
            elif event == 'push' and find_key("created", data) and not find_key("deleted", data) \
                    and not find_key("forced", data) and find_key("base_ref", data):
                print("NEW BRANCH")
                pprint.pprint(data)
                get_new_branch = GetBranch(db)
                get_new_branch.get_data(data)

    def start(self):
        workers = [Thread(target=self.webhook_event_router, args=()) for _ in range(1)]
        [t.start() for t in workers]
