import functools
from asyncio import iscoroutinefunction, iscoroutine


class Defer:
    def __init__(self):
        self.deferred_calls = []

    def defer(self, func, *args, **kwargs):
        self.deferred_calls.insert(0, (func, args, kwargs))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for func, args, kwargs in self.deferred_calls:
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Error executing deferred function {func.__name__}: {e}")


class AsyncDefer:
    def __init__(self):
        self.deferred_calls = []

    def defer(self, func, *args, **kwargs):
        self.deferred_calls.insert(0, (func, args, kwargs))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        deferred_exception = None
        for func, args, kwargs in self.deferred_calls:
            try:
                result = func(*args, **kwargs)
                if iscoroutine(result):
                    await result
            except Exception as e:
                if deferred_exception is None:
                    deferred_exception = e
                else:
                    print(f"Error executing deferred function {func.__name__}: {e}")

        if exc_type:
            return False
        if deferred_exception:
            raise deferred_exception
        return True


def defer(func):
    if iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            async with AsyncDefer() as d:
                def defer_func(func_to_call, *defer_args, **defer_kwargs):
                    d.defer(lambda: func_to_call(*defer_args, **defer_kwargs))

                kwargs['defer'] = defer_func

                result = await func(*args, **kwargs)

                return result
        return async_wrapper

    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with Defer() as d:
                def defer_func(func_to_call, *defer_args, **defer_kwargs):
                    d.defer(func_to_call, *defer_args, **defer_kwargs)

                kwargs['defer'] = defer_func

                result = func(*args, **kwargs)

                return result
        return sync_wrapper
