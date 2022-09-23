import timeit
from units.redis_lru import *

client = redis.Redis(host="localhost", port=6379)
cache = MyLRU(client, max_size=512, clear_on_start=True)


def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


@cache
def fibonacci_cache(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_cache(n - 1) + fibonacci_cache(n - 2)


if __name__ == '__main__':

    start_time = timeit.default_timer()
    n = 38
    print(f'fibonacci({n}) -> {fibonacci(n)}')
    print(f'Duration without LRU cache: {timeit.default_timer() - start_time} sec')

    start_time = timeit.default_timer()
    n = 380
    print(f'fibonacci({n}) -> {fibonacci_cache(n)}')
    print(f'Duration with LRU cache: {timeit.default_timer() - start_time} sec')

