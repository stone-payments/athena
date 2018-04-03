from collection_modules.module import find_key
from webhook.webhook_get_commit import GetCommit
from threading import Thread


class WebhookEventRouter:

    def __init__(self, webhook_queue):
        self.webhook_queue = webhook_queue

    def webhook_event_router(self):
        while True:
            returned_data = self.webhook_queue.get(block=True)
            event = returned_data[0]
            data = returned_data[1]
            if event == 'push' and find_key("deleted", data) is False:
                get_commit = GetCommit()
                get_commit.get_data(data)
                modified_file = find_key("modified", data)
                print(modified_file)
                if "README.md" in modified_file or "readme.md" in modified_file:
                    print("Entrou")

                if "CHANGELOG.md" in modified_file:
                    print("Entrou changelog")

    def start(self):
        workers = [Thread(target=self.webhook_event_router, args=()) for _ in range(1)]
        [t.start() for t in workers]
