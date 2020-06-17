from typing import Any, Optional, Union

XML: str
JSON: str
JSONLD: str
TURTLE: str
N3: str
RDF: str
RDFXML: str
CSV: str
TSV: str
GET: str
POST: str
BASIC: str
DIGEST: str
SELECT: str
CONSTRUCT: str
ASK: str
DESCRIBE: str
INSERT: str
DELETE: str
CREATE: str
CLEAR: str
DROP: str
LOAD: str
COPY: str
MOVE: str
ADD: str
URLENCODED: str
POSTDIRECTLY: str

class SPARQLWrapper:
    def __init__(
        self,
        endpoint: Any,
        updateEndpoint: Optional[Any] = ...,
        returnFormat: Any = ...,
        defaultGraph: Optional[Any] = ...,
        agent: Any = ...,
    ) -> None: ...
    def setQuery(self, query: Union[str, bytes]) -> None: ...
    def query(self) -> QueryResult: ...

class QueryResult:
    def convert(self) -> Any: ...
