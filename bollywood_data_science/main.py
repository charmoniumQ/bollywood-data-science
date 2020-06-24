from typing import Set
import charmonium.time_block as ch_time_block
import yaml
import sys

from .imdb_graph import imdb_graph
from .sparql_graph import cached_sparql_graph


def is_int(string: str):
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True


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
        imdb_ids: Set[str] = set()
        for person, imdb_id_ in graph.query(
                "SELECT DISTINCT ?person ?personImdbId WHERE { ?person wdt:P345 ?personImdbId }"
        ):
            imdb_id = str(imdb_id_)
            if not is_int(imdb_id[2:]):
                print(f"Bad IMDDb id ({imdb_id}) for {person}")
            else:
                imdb_ids.add(imdb_id)
        imdb_ids = sorted(imdb_ids)

    print(dict(triples=len(graph), people=len(people), imdb_ids=len(imdb_ids),))
    start = int(sys.argv[1])
    stop  = int(sys.argv[2])
    graph_imdb = imdb_graph(imdb_ids[start:stop], db=False)
    print(dict(graph_imdb=len(graph_imdb)))


if __name__ == "__main__":
    main()
