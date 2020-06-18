import logging
import re
import sys
import urllib.parse
from typing import Any, Dict, Optional, cast

import charmonium.cache as ch_cache
import rdflib
import requests
import yaml

from .time_code import time_code

logging.basicConfig(level=logging.DEBUG)


def _cached_sparql_graph(
    endpoint: str,
    query: str,
    return_format: str = "XML",
    headers: Optional[Dict[str, str]] = None,
    method: str = "POST",
    params: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> rdflib.Graph:
    """Query a SPARQL endpoint, but cache the resulting RDF"""

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


# ch_cache.decor is CachedFunc -> Cache[CachedFunc], where CachedFunc is a TypeVar.
# This is a good start, however ch_cache.Cache[func].__call__ is Any -> Any.
# Therefore, when I wrap my function with the cache decorator, it
# "forgets" tye type of the original callable.  If that were better
# typed, then this is unnecessary
class _CacheSparqlGraph:
    def __call__(
        self,
        endpoint: str,
        query_string: str,
        return_format: str = "XML",
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Dict[str, Any],
    ) -> rdflib.Graph:
        ...


cached_sparql_graph = cast(
    _CacheSparqlGraph,
    time_code.decor(run_gc=True)(
        ch_cache.decor(ch_cache.DirectoryStore.create("tmp"))(_cached_sparql_graph)
    ),
)


def get_dataset() -> rdflib.Graph:
    with open("res/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    query_name = "wikidata_get"

    endpoint = config["queries"][query_name]["endpoint"]
    query = config["queries"][query_name]["query"]
    if config["queries"][query_name].get("minify", False):
        query = re.sub(r"\s+", " ", query.strip())
    return_format = config["queries"][query_name]["return_format"]
    headers = config["queries"][query_name]["headers"]
    method = config["queries"][query_name]["method"]
    graph = cached_sparql_graph(
        endpoint, query, return_format=return_format, headers=headers, method=method,
    )
    return graph


if __name__ == "__main__":

    def main() -> None:
        for subj, verb, obj in get_dataset():
            pass
            # print(f'{subj} <-{verb}-> {obj}')

    main()
