#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper, wraps


def disable(func):
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    """

    def wrapper(*args, **kwds):
        cache = getattr(wrapper, 'calls', 0) + 1
        update_wrapper(wrapper, func, updated={'cache': {}})

        return func(*args, **kwds)

    return wrapper


def decorator(f):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """

    @wraps(f)
    def wrapper(*args, **kwds):
        return f(*args, **kwds)

    return wrapper


def countcalls(func):
    """Decorator that counts calls made to the function decorated."""

    @wraps(func)
    def wrapper(*args):
        wrapper.calls = getattr(wrapper, 'calls', 0) + 1
        return func(*args)

    return wrapper


def memo(func):
    """
    Memoize a function so that it caches all return values for
    faster future lookups.
    """
    cache = {}

    def memoized(*args):
        update_wrapper(memoized, func)
        if args in cache:
            return cache[args]
        else:
            result = cache[args] = func(*args)
            return result

    return memoized


def n_ary(func):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    """

    def wrapper(*args):
        ar_len = len(args)
        if ar_len == 1:
            res = func(args[0], 0)
        elif ar_len == 2:
            res = func(args[0], args[1])
        else:
            res = func(args[0], func(args[1], args[2]))

        return res

    return wrapper


def trace(pat):
    """Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    """

    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f'{pat}--> {func.__name__}({args[0]})')
            return_value = func(*args, **kwargs)
            print(f'{pat}<-- {func.__name__}({args[0]}) == {return_value}')
            return return_value

        return wrapper

    return actual_decorator


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@memo
@countcalls
@n_ary
def bar(a, b):
    return a * b


@memo
@countcalls
@trace("####")
@decorator
# @disable
def fib(n):
    """Fibonacci function"""
    return 1 if n <= 1 else fib(n - 1) + fib(n - 2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    fib(3)
    print(fib.__doc__)
    # print("fib", fib.calls, 'calls made')


if __name__ == '__main__':
    main()
