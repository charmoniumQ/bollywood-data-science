from typing import Any, Optional

sync_open = open

def open(
    file: Any,
    mode: str = ...,
    buffering: int = ...,
    encoding: Optional[Any] = ...,
    errors: Optional[Any] = ...,
    newline: Optional[Any] = ...,
    closefd: bool = ...,
    opener: Optional[Any] = ...,
    *,
    loop: Optional[Any] = ...,
    executor: Optional[Any] = ...,
) -> Any: ...
