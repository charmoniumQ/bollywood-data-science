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
    return_format: str = "XML",
    headers: Optional[Dict[str, str]] = None,
    method: str = "POST",
    params: Optional[Dict[str, str]] = None,
    minify: bool = False,
    **kwargs: Any,
) -> rdflib.Graph:
    """Query a SPARQL endpoint, but cache the resulting RDF"""

    if minify:
        query = re.sub(r"\s+", " ", query.strip())

    headers_ = headers if headers else dict()
    params_ = params if params else dict()

    # This ensures sure I never use params where I meant params_
    del headers, params

    if method == "POST":
        http_rsp = requests.post(
            url=endpoint,
            headers=headers_,
            data="query=" + urllib.parse.quote(query),
            **kwargs,
        )
    elif method == "GET":
        http_rsp = requests.get(
            url=endpoint, headers=headers_, params={"query": query, **params_}, **kwargs
        )
    else:
        raise RuntimeError(f"Method {method} is not supported (GET, POST)")

    try:
        http_rsp.raise_for_status()
    except requests.HTTPError:
        print(http_rsp.text, file=sys.stderr)

    text_req = http_rsp.text

    if rdflib.plugin.get(return_format, rdflib.parser.Parser):
        graph = rdflib.Graph()
        graph.parse(data=text_req, format=return_format)
        return graph
    else:
        raise RuntimeError(f"rdflib has no plugin for {return_format}")


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
