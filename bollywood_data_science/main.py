import charmonium.time_block as ch_time_block
import yaml

from .imdb_graph import imdb_graph
from .sparql_graph import cached_sparql_graph


def main() -> None:
    with open("res/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    query_name = "wikidata_get"

    endpoint = config["queries"][query_name]["endpoint"]
    query = config["queries"][query_name]["query"]
    config["queries"][query_name].get("minify", False)
    return_format = config["queries"][query_name]["return_format"]
    headers = config["queries"][query_name]["headers"]
    method = config["queries"][query_name]["method"]
    graph = cached_sparql_graph(
        endpoint, query, return_format=return_format, headers=headers, method=method,
    )

    with ch_time_block.ctx("selecting"):
        people = {
            "1"
            # str(row[0])
            # for row in graph.query(
            #     "SELECT DISTINCT ?person WHERE { ?person ?prop ?thing }"
            # )
        }
        imdb_ids = {
            "1"
            # str(row[0])
            # for row in graph.query(
            #     "SELECT DISTINCT ?personImdbId WHERE { ?person wdt:P345 ?personImdbId }"
            # )
        }
    print(dict(triples=len(graph), people=len(people), imdb_ids=len(imdb_ids),))
    graph_imdb = imdb_graph(imdb_ids)
    print(dict(graph_imdb=len(graph_imdb)))


if __name__ == "__main__":
    main()
