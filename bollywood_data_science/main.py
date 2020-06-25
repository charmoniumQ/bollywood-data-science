import sys
from typing import Dict, cast

import charmonium.time_block as ch_time_block
import rdflib
import yaml

from .imdb_graph import imdb_graph
from .sparql_graph import cached_sparql_graph


def is_int(string: str) -> bool:
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True


def main() -> None:
    with open("res/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    graph = cached_sparql_graph(**config["queries"]["wikidata_get"])

    with ch_time_block.ctx("selecting"):
        people = {
            str(row[0])
            for row in graph.query(
                "SELECT DISTINCT ?person WHERE { ?person ?prop ?thing }"
            )
        }
        imdb_ids_: Dict[rdflib.term.Node, str] = dict()
        for person_, imdb_id_ in graph.query(
            "SELECT DISTINCT ?person ?personImdbId WHERE { ?person wdt:P345 ?personImdbId }"
        ):
            person = cast(rdflib.term.Node, person_)  # type: ignore
            imdb_id = cast(str, imdb_id_.toPython())  # type: ignore
            if not is_int(imdb_id[2:]):
                print(f"Bad IMDDb id ({imdb_id}) for {person}")
            else:
                imdb_ids_[person] = imdb_id
        imdb_ids = sorted(imdb_ids_.items())

    print(dict(triples=len(graph), people=len(people), imdb_ids=len(imdb_ids),))

    if len(sys.argv) == 3:
        start, stop = map(int, sys.argv[1:3])
        imdb_graph(imdb_ids[start:stop], db=False)
    else:
        divisions = list(range(0, len(imdb_ids), len(imdb_ids) // 15))
        print("\n".join(map(str, (enumerate(zip(divisions[:-1], divisions[1:]))))))
        # graph_imdb = rdflib.Graph()
        # for start, stop in zip(divisions[:-1], divisions[1:]):
        #     graph_imdb += imdb_graph(imdb_ids[start:stop], db=False)


if __name__ == "__main__":
    main()
