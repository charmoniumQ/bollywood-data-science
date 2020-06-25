import csv
import io
import time
import re
import sys
import urllib.parse
from typing import Callable, Dict, List, Optional, cast

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


def sparql_select(
    endpoint: str,
    query: str,
    return_format: str = "csv",
    headers: Optional[Dict[str, str]] = None,
    method: str = "POST",
    params: Optional[Dict[str, str]] = None,
    minify: bool = False,
) -> List[List[str]]:
    """Query a SPARQL endpoint, but cache the resulting RDF"""

    if minify:
        query = re.sub(r"\s+", " ", query.strip())

    headers_ = headers if headers else dict()
    params_ = params if params else dict()

    # This ensures sure I never use params where I meant params_
    del headers, params

    if method == "POST":
        http_rsp = requests.post(
            url=endpoint, headers=headers_, data="query=" + urllib.parse.quote(query),
        )
    elif method == "GET":
        http_rsp = requests.get(
            url=endpoint, headers=headers_, params={"query": query, **params_}
        )
    else:
        raise RuntimeError(f"Method {method} is not supported (GET, POST)")

    try:
        http_rsp.raise_for_status()
    except requests.HTTPError:
        print(http_rsp.text, file=sys.stderr)

    if return_format == "csv":
        return list(csv.reader(io.StringIO(http_rsp.text)))
    else:
        raise NotImplementedError(f"Not implemented for {return_format}")


def wikidata_label(full_item: str) -> str:
    # https://stackoverflow.com/questions/59737076/how-to-get-a-label-of-a-property-from-wikidata
    item = full_item.split("/")[-1]
    if item.startswith("P"):
        results = sparql_select(
            "https://query.wikidata.org/sparql",
            """
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX bd: <http://www.bigdata.com/rdf#>
            SELECT ?wdLabel WHERE {
                VALUES (?wdt) {(wdt:P131)}
                ?wd wikibase:directClaim ?wdt .
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }""",
            return_format="csv",
            headers={
                "Accept": "text/csv",
                "User-Agent": "BOT (github.com/charmoniumQ/bollywood-data-science; sam@samgrayson.me)",
            },
            method="GET",
            params={},
            minify=True,
        )
        time.sleep(0.5)
        assert results[0] == ['wdLabel']
        return results[1][0]
    elif item.startswith("Q"):
        return full_item
    else:
        raise ValueError("Unknown Wikidata type")


cached_wikidata_label = cast(
    Callable[[str], str], ch_cache.decor(ch_cache.FileStore.create("tmp"))(wikidata_label)
)

cached_wikidata_label.disable_logging() # type: ignore
