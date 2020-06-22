import abc
from typing import Any, Mapping

class IMDb:
    def __init__(self, method: str = ..., path: str = ...) -> None: ...
    def get_person(self, id: str) -> Person: ...
    def get_movie(self, id: str) -> Movie: ...

class Person(Mapping[str, Any], metaclass=abc.ABCMeta): ...
class Movie(Mapping[str, Any], metaclass=abc.ABCMeta): ...
