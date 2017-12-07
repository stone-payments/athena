from module import *
import time
from config import *


class Pagination:
    def __init__(self,
                 query: object,
                 number_of_repo: object = None,
                 next_cursor: object = None,
                 next_repo: object = None,
                 org: object = None,
                 slug: object = None,
                 since: type = since_time,
                 until: type = until_time,
                 edges_name: object = 'edges'):
        self.query = query
        self.number_of_repo = number_of_repo
        self.next_cursor = next_cursor
        self.next_repo = next_repo
        self.org = org
        self.slug = slug
        self.since = since
        self.until = until
        self.edges_name = edges_name

    def __iter__(self):
        self.has_next_page = True
        self.cursor = None
        return self

    def __next__(self):
        if self.has_next_page:
            time.sleep(abuse_time_sleep)
            return self.__next_page()
        else:
            raise StopIteration()

    def __next_page(self):
        response = pagination_universal(self.query, number_of_repo=self.number_of_repo, next_cursor=self.cursor,
                                        org=self.org, since=self.since(since_time_days_delta),
                                        until=self.until(until_time_days_delta), slug=self.slug,
                                        next_repo=self.next_repo)
        limit_validation(rate_limit=find('rateLimit', response))
        self.has_next_page = find('hasNextPage', response)
        self.cursor = find('endCursor', response)
        return response
