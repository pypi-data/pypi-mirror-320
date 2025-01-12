import time
from concurrent.futures import ThreadPoolExecutor


def prefetch_iterator(iterator):
    with ThreadPoolExecutor(1) as p:
        iterator = iter(iterator)
        prefetched = p.submit(next, iterator)
        while True:
            try:
                rets = prefetched.result()
            except StopIteration:
                break
            prefetched = p.submit(next, iterator)
            yield rets


def rate_limit_iterator(iterator, iters_per_second):
    start = time.time()
    for i, it in enumerate(iterator):
        yield it
        time.sleep(max(0, (i / iters_per_second) - (time.time() - start)))
