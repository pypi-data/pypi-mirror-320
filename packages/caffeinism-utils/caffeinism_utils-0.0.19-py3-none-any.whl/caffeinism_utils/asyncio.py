import asyncio
import collections
import contextlib
import logging
from abc import ABC
from functools import partial, update_wrapper, wraps

logger = logging.getLogger(__name__)


class Function(ABC):
    def __get__(self, instance, instancetype):
        return partial(self.__call__, instance)


class run_in_threadpool(Function):
    def __init__(self, func, *args, **kwargs):
        update_wrapper(self, func)
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return run_in_executor(None, self.__func, *args, **kwargs)

    def __await__(self):
        result = yield from run_in_executor(
            None, self.__func, *self.__args, **self.__kwargs
        ).__await__()
        return result


class run_in_executor(Function):
    def __init__(self, pool, func=None, *args, **kwargs):
        self.__pool = pool
        self.__func = func and partial(func, *args, **kwargs)
        if func is not None:
            update_wrapper(self, func)

    def __call__(self, func):
        assert self.__func is None

        @wraps(func)
        def _func(*args, **kwargs):
            loop = asyncio.get_running_loop()
            callable = partial(func, *args, **kwargs)
            return loop.run_in_executor(self.__pool, callable)

        return _func

    def __await__(self):
        assert self.__func is not None
        loop = asyncio.get_running_loop()
        result = yield from loop.run_in_executor(self.__pool, self.__func).__await__()
        return result


class LastManStanding:
    class __Defeat(Exception):
        pass

    def __init__(self):
        self.__locks = collections.defaultdict(asyncio.Lock)
        self.__counter = collections.defaultdict(int)

    @contextlib.asynccontextmanager
    async def join(self, key):
        with contextlib.suppress(LastManStanding.__Defeat):
            yield self.__wait(key)

    @contextlib.asynccontextmanager
    async def __wait(self, key):
        self.__counter[key] += 1
        async with self.__locks[key]:
            self.__counter[key] -= 1
            if self.__counter[key]:
                raise LastManStanding.__Defeat
            else:
                yield
