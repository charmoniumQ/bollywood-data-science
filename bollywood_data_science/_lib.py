from typing import Any, Dict, cast

import charmonium.cache as ch_cache
import rdflib
from SPARQLWrapper import SPARQLWrapper, Wrapper


@ch_cache.decor(ch_cache.DirectoryStore.create("tmp"))
def cached_sparql_graph(
    endpoint: str, query_string: str, **kwargs: Dict[str, Any]
) -> rdflib.Graph:
    """Query a SPARQL endpoint, but cache the resulting RDF"""
    sparql_req = SPARQLWrapper(
        endpoint=endpoint, returnFormat=Wrapper.JSONLD, **kwargs,
    )
    sparql_req.setQuery(query_string)
    query_result = sparql_req.query()
    graph = query_result.convert()
    return cast(rdflib.Graph, graph)
