from .term import URIRef

class Namespace(str):
    def term(self, term: str) -> URIRef: ...
