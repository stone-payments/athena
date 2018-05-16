import time

from collection_modules.log_message import log
from collection_modules.module import utc_time, client_graphql, find_key, limit_validation
from custom_configurations.config import abuse_time_sleep, since_time_days_delta, until_time_days_delta


class Pagination:
    def __init__(self,
                 query: object,
                 number_of_repo: int,
                 next_cursor: str = None,
                 next_repo: str = None,
                 org: str = None,
                 slug: str = None,
                 updated_time: callable = utc_time,
                 edges_name: str = 'edges'):
        self.query = query
        self.number_of_repo = number_of_repo
        self.next_cursor = next_cursor
        self.next_repo = next_repo
        self.org = org
        self.slug = slug
        self.time = updated_time
        self.edges_name = edges_name

    def __iter__(self):
        self.__has_next_page = True
        self.__cursor = None
        return self

    def __next__(self):
        if self.__has_next_page:
            time.sleep(abuse_time_sleep)
            return self.__next_page()
        else:
            raise StopIteration()

    def __pagination_universal(self):
        response_page = client_graphql.execute(self.query,
                                               {
                                                   "number_of_repos": self.number_of_repo,
                                                   "next": self.__cursor,
                                                   "next2": self.next_repo,
                                                   "org": self.org,
                                                   "slug": self.slug,
                                                   "sinceTime": self.time(since_time_days_delta),
                                                   "untilTime": self.time(until_time_days_delta)
                                               })
        if find_key('errors', response_page) is not None:
            log.error(response_page)
        log.info(find_key('hasNextPage', response_page))
        return response_page

    def __next_page(self):
        __response = self.__pagination_universal()
        limit_validation(rate_limit=find_key('rateLimit', __response))
        self.__has_next_page = find_key('hasNextPage', __response)
        self.__cursor = find_key('endCursor', __response)
        return __response
