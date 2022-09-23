import redis
from functools import wraps
import types
import pickle


class ArgsUnhashable(Exception):
    pass


class MyLRU:
    def __init__(self, client: redis.Redis,
                 max_size=2 ** 20,
                 key_prefix='MyRedisLRU',
                 clear_on_start=False):
        self.client = client
        self.max_size = max_size
        self.key_prefix = key_prefix

        if clear_on_start:
            self.client.flushdb()
        elif self.client.exists('CashList'):
            while self.client.llen('CashList') > self.max_size:
                key = self.client.rpop('CashList')
                self.client.delete(key)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = self._decorator_key(func, *args, **kwargs)
            if self.client.exists(key):
                result = self.client.get(key)
                result = pickle.loads(result)
                self.move_up(key)
            else:
                result = func(*args, **kwargs)
                self.add(key, result)

            return result

        return wrapper

    def _decorator_key(self, func: types.FunctionType, *args, **kwargs):
        try:
            hash_arg = tuple([hash(arg) for arg in args])
            hash_kwargs = tuple([hash(value) for value in kwargs.values()])
        except TypeError as err:
            raise ArgsUnhashable()

        return f'{self.key_prefix}:{func.__module__}:{func.__qualname__}{hash_arg}:{hash_kwargs}'

    def move_up(self, key):
        self.client.lrem('CashList', 1, key)
        self.client.lpush('CashList', key)

    def add(self, key, value):
        value = pickle.dumps(value)
        self.client.set(key, value)
        self.client.lpush('CashList', key)
        if self.client.llen('CashList') > self.max_size:
            key = self.client.rpop('CashList')
            self.client.delete(key)


if __name__ == '__main__':
    pass
