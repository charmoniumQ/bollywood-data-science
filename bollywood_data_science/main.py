import yaml

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
    people = set()
    for subj, _verb, _obj in graph:
        people.add(subj)
    print(dict(triples=len(graph), people=len(people)))


if __name__ == "__main__":
    main()
