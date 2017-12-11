import time


class Retry:
    def __init__(self, request, interval, times):
        self.request = request
        self.interval = interval
        self.times = times

    def __call__(self, *args, **kwargs):
        for t in range(self.times):
            try:
                return self.request(*args, **kwargs)
            except TimeoutError as e:
                if t == self.times - 1:
                    raise e
            time.sleep(self.interval)


def retry(obj, interval, retries):
    for method in [m for m in dir(obj) if not m.startswith('__')]:
        setattr(obj, method, Retry(getattr(obj, method), interval, retries))
    return obj
