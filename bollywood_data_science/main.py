import collections
import csv
import itertools
import sys
from typing import Dict, List, cast, Optional, IO, TypeVar, Mapping, Iterable

import charmonium.time_block as ch_time_block
import rdflib
from tqdm import tqdm

from .imdb_graph import imdb_graph
from .sparql_graph import cached_sparql_graph, cached_wikidata_label
from .disjoint_set import DisjointSet


def is_int(string: str) -> bool:
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True


def main() -> None:
    person_filter = """
        ?person wdt:P106 wd:Q33999 .
        {
          { ?person wdt:P27 wd:Q668 . } UNION
          { ?person wdt:P19/wdt:P17 wd:Q668 . } UNION
          { ?person wdt:P19/wdt:P17? wd:Q129286 . } .
        } .
        """.replace("\n        ", "\n")[1:-1]
    info_query = """
      PREFIX wd: <http://www.wikidata.org/entity/>
      PREFIX wdt: <http://www.wikidata.org/prop/direct/>
      CONSTRUCT {
        ?person wdt:P21 ?sex .
        ?person wdt:P345 ?personImdbId .
        ?person wdt:P19 ?placeOfBirth .
        ?person wdt:P69 ?school .
        ?person wdt:P551 ?residence .
        ?person wdt:172 ?ethnicGroup .
        ?person wdt:149 ?religion .
        ?person wdt:1412 ?langauage .
        ?person wdt:P39 ?positionHeld .
      } WHERE {
        person_filter
        OPTIONAL { ?person wdt:P21 ?sex . } .
        OPTIONAL { ?person wdt:P345 ?personImdbId . } .
        OPTIONAL { ?person wdt:P19 ?placeOfBirth . } .
        OPTIONAL { ?person wdt:P69 ?school . } .
        OPTIONAL { ?person wdt:P551 ?residence . } .
        OPTIONAL { ?person wdt:172 ?ethnicGroup . } .
        OPTIONAL { ?person wdt:149 ?religion . } .
        OPTIONAL { ?person wdt:1412 ?langauage . } .
        OPTIONAL { ?person wdt:P39 ?positionHeld . } .
      }
      """.replace("\n      ", "\n").replace("person_filter", person_filter)[1:-1]

    params = dict(
        minify=True,
        headers={"Accept": "text/plain", "User-Agent": "BOT (github.com/charmoniumQ/bollywood-data-science; sam@samgrayson.me)"},
        return_format="n3",
        method="POST",
        endpoint="https://query.wikidata.org/sparql",
        params={},
    )
    info_graph = cached_sparql_graph(
        query=info_query,
        **params
    )

    family_query = """
      PREFIX wd: <http://www.wikidata.org/entity/>
      PREFIX wdt: <http://www.wikidata.org/prop/direct/>
      CONSTRUCT {
        ?person wdt:P22 ?father .
        ?person wdt:P25 ?mother .
        ?person wdt:P3448 ?stepparent .
        ?person wdt:PP1038 ?relative .
        ?person wdt:P3373 ?sibling .
        ?person wdt:P26 ?spouse .
        ?person wdt:P40 ?child .
      } WHERE {
        person_filter
        OPTIONAL { ?person wdt:P22 ?father . } .
        OPTIONAL { ?person wdt:P25 ?mother . } .
        OPTIONAL { ?person wdt:P3448 ?stepparent } .
        OPTIONAL { ?person wdt:PP1038 ?relative } .
        OPTIONAL { ?person wdt:P3373 ?sibling . } .
        OPTIONAL { ?person wdt:P26 ?spouse . } .
        OPTIONAL { ?person wdt:P40 ?child . } .
      }
      """.replace("\n      ", "\n").replace("person_filter", person_filter)[1:-1]

    familial_graph = cached_sparql_graph(
        query=family_query,
        **params
    )

    with ch_time_block.ctx("selecting"):
        people = {
            person.toPython()
            for person, prop, thing in info_graph
        }
        imdb_ids_: Dict[rdflib.term.Node, str] = dict()
        for person_, imdb_id_ in info_graph.query(
            "SELECT DISTINCT ?person ?personImdbId WHERE { ?person wdt:P345 ?personImdbId }"
        ):
            person = cast(rdflib.term.Node, person_)  # type: ignore
            imdb_id = cast(str, imdb_id_.toPython())  # type: ignore
            if not is_int(imdb_id[2:]):
                print(f"Bad IMDDb id ({imdb_id}) for {person}")
            else:
                imdb_ids_[person] = imdb_id
        imdb_ids = sorted(imdb_ids_.items())

    print(dict(triples=len(info_graph), people=len(people), imdb_ids=len(imdb_ids),))

    if len(sys.argv) == 3:
        start, stop = map(int, sys.argv[1:3])
        imdb_graph(imdb_ids[start:stop], db=False)
    else:
        divisions = list(range(0, len(imdb_ids), 700))
        for start, stop in zip(divisions[:-1], divisions[1:]):
            info_graph += imdb_graph(imdb_ids[start:stop], db=False)
        person_info_records = graph_to_records(info_graph)
        with open("all.csv", "w+") as f:
            records_to_csv(person_info_records, f)

        def family_weight(family: Iterable[rdflib.term.Node]) -> int:
            return sum(person in person_info_records.keys() for person in family)

        families_uf: DisjointSet[rdflib.term.Node] = DisjointSet()
        for person, _, relative in familial_graph:
            families_uf.add(person, relative)
        name_col = cast(rdflib.term.Node, rdflib.term.URIRef("https://imdb.com/name"))
        with open("families.txt", "w+") as f:
            families = sorted(families_uf.group.values(), key=family_weight, reverse=True)
            for family in families:
                print(len(family), file=f)
                for member in family:
                    if member in person_info_records:
                        name = str(person_info_records[member][name_col])
                        prefix = '*'
                    else:
                        name = ''
                        prefix = ' '
                    print(prefix, str(member), name, file=f)

@ch_time_block.decor()
def records_to_csv(records: Dict[rdflib.term.Node, Dict[rdflib.term.Node, List[rdflib.term.Node]]], file_: IO[str]) -> None:
    name_col = cast(rdflib.term.Node, rdflib.term.URIRef("https://imdb.com/name"))
    imdb_col = cast(
        rdflib.term.Node, rdflib.term.URIRef("http://www.wikidata.org/prop/direct/P345")
    )
    cols_set = set(key for record in records.values() for key in record.keys())

    cols = [name_col, imdb_col] + sorted(
        cols_set - {name_col, imdb_col}
    )

    csvw = csv.writer(file_)
    csvw.writerow(["Wikidata ID", *map(rdf_term_to_str, cols)])
    for wikidata_id, person in tqdm(records.items()):
        csvw.writerow(
            [rdf_term_to_str(wikidata_id), *(" ".join(map(rdf_term_to_str, person.get(col, []))) for col in cols)]
        )


def rdf_term_to_str(term: rdflib.term.Node) -> str:
    if isinstance(term, rdflib.term.URIRef):
        py_url = cast(str, term.toPython())
        if py_url.startswith("https://imdb.com/"):
            return py_url[17:]
        elif py_url.startswith("http://www.wikidata.org/"):
            # return cached_wikidata_label(py_url)
            return py_url
        else:
            return py_url
    else:
        py_term = term.toPython()
        if isinstance(py_term, str):
            if py_term.startswith("nm"):
                return f"https://www.imdb.com/name/{py_term}"
            elif py_term.startswith("tt"):
                return f"https://www.imdb.com/title/{py_term}"
            else:
                return py_term
        else:
            return str(py_term)


@ch_time_block.decor()
def graph_to_records(
        graph: rdflib.Graph,
) -> Dict[rdflib.term.Node, Dict[rdflib.term.Node, List[rdflib.term.Node]]]:

    subject_dicts: Dict[
        rdflib.term.Node, Dict[rdflib.term.Node, List[rdflib.term.Node]]
    ] = collections.defaultdict(lambda: collections.defaultdict(list))

    for subject, verb, object in tqdm(graph):
        subject_dicts[subject][verb].append(object)

    return subject_dicts


if __name__ == "__main__":
    main()
