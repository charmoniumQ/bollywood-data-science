from typing import IO, Any, Dict, Iterator, Optional, Tuple, Union

from .query import Result
from .term import Node

class Graph(Node):
    def serialize(
        self,
        destination: Optional[str] = None,
        format: str = "xml",
        encoding: Optional[str] = None,
        **args: Any,
    ) -> str: ...
    def parse(
        self,
        source: Optional[Union[str, IO[str]]] = None,
        publicID: Optional[str] = None,
        format: Optional[str] = None,
        location: Optional[str] = None,
        file: Optional[IO[str]] = None,
        data: Optional[str] = None,
    ) -> None: ...
    def __iter__(self) -> Iterator[Any]: ...
    def __len__(self) -> int: ...
    def add(self, triple: Tuple[Node, Node, Node]) -> None: ...
    def query(self, query_str: str) -> Result: ...
