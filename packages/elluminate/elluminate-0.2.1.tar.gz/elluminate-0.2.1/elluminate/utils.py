import asyncio
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar, cast

from httpx import HTTPStatusError, Response


def raise_for_status_with_detail(response: Response) -> None:
    """Raises HTTPStatusError with detailed error message from response if status code is non-2XX.
    Falls back to standard error message if no detail is found.
    """
    try:
        response.raise_for_status()
    except HTTPStatusError as e:
        try:
            error_detail = response.json().get("detail", str(e))
            raise HTTPStatusError(message=error_detail, request=response.request, response=response) from e
        except ValueError:  # JSON decode error
            raise e


T = TypeVar("T")
P = ParamSpec("P")


def run_async(async_func: Callable[P, Awaitable[T]]) -> Callable[P, T]:
    """Utility function to run an async function in a synchronous context."""

    @wraps(async_func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_event_loop()
        return cast(T, loop.run_until_complete(async_func(*args, **kwargs)))

    return sync_wrapper
