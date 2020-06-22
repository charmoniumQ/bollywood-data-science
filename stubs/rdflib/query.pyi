from typing import Any, Iterator

class Result:
    def __iter__(self) -> Iterator[ResultRow]: ...

class ResultRow:
    def __getitem__(self, index: int) -> Any: ...
