from collections.abc import Coroutine
from types import coroutine as coroutine
from typing import Any, Optional

class AsyncBase:
    def __init__(self, file: Any, loop: Any, executor: Any) -> None: ...
    def __aiter__(self): ...
    async def __anext__(self): ...

class _ContextManager(Coroutine):
    def __init__(self, coro: Any) -> None: ...
    def send(self, value: Any): ...
    def throw(self, typ: Any, val: Optional[Any] = ..., tb: Optional[Any] = ...): ...
    def close(self): ...
    @property
    def gi_frame(self): ...
    @property
    def gi_running(self): ...
    @property
    def gi_code(self): ...
    def __next__(self): ...
    @coroutine
    def __iter__(self) -> Any: ...
    def __await__(self): ...
    async def __anext__(self): ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None: ...

class AiofilesContextManager(_ContextManager):
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...