import os
import re
import sys
import urllib.parse
from typing import Any, Callable, Dict, Optional, cast

import charmonium.cache as ch_cache
import charmonium.time_block as ch_time_block
import rdflib
import requests


def sparql_graph(
    endpoint: str,
    query: str,
    return_format: str,
    headers: Dict[str, str],
    method: str,
    params: Dict[str, str],
    minify: bool,
) -> rdflib.Graph:
    """Query a SPARQL endpoint, but cache the resulting RDF"""

    if minify:
        query = re.sub(r"\s+", " ", query.strip())

    if "CONSTRUCT" not in query:
        raise ValueError("Must be a CONSTRUCT query")

    graph = rdflib.Graph()
    url = endpoint + "?query=" + urllib.parse.quote_plus(query)
    graph.parse(url)
    return graph

cached_sparql_graph = cast(
    Callable[..., rdflib.Graph],
    ch_time_block.decor()(
        ch_cache.decor(
            ch_cache.DirectoryStore.create("tmp"),
            verbose=True,
            name="cache_sparql_graph",
        )(sparql_graph)
    ),
)
