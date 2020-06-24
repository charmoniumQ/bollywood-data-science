import charmonium.time_block as ch_time_block
import yaml
import sys

from .imdb_graph import imdb_graph
from .sparql_graph import cached_sparql_graph


def main() -> None:
    with open("res/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    graph = cached_sparql_graph(
        **config["queries"]["wikidata_get"]
    )

    with ch_time_block.ctx("selecting"):
        people = {
            str(row[0])
            for row in graph.query(
                "SELECT DISTINCT ?person WHERE { ?person ?prop ?thing }"
            )
        }
        imdb_ids = {
            str(row[0])
            for row in graph.query(
                "SELECT DISTINCT ?personImdbId WHERE { ?person wdt:P345 ?personImdbId }"
            )
        }
    print(dict(triples=len(graph), people=len(people), imdb_ids=len(imdb_ids),))
    imdb_ids = sorted(imdb_ids)
    args = dict(enumerate(sys.argv))
    start = args.get(1)
    stop  = args.get(2)
    graph_imdb = imdb_graph(imdb_ids[start:stop], db=False)
    print(dict(graph_imdb=len(graph_imdb)))


if __name__ == "__main__":
    main()
