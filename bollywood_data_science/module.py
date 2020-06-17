import rdflib
import requests


def query_wikidata(sparql_query: str) -> None:
    r = requests.get(
        "https://query.wikidata.org/sparql",
        data=query,
        headers={
            "Content-Type": "application/sparql-query",
            "Accept": "application/sparql-results+json",
        },
    )

    print(r.text)


def get_bollywood_actors():
    # create empty graph
    g = rdflib.Graph()


# execute SPARQL CONSTRUCT query to get a set of RDF triples
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.addDefaultGraph("http://dbpedia.org")
query = """
    PREFIX dbpedia: <http://dbpedia.org/resource/> 
    CONSTRUCT { 
     ?s rdf:type dbo:PopulatedPlace. 
     ?s dbp:iso3166code ?code. 
     ?s dbo:populationTotal ?pop. 
    } WHERE{ 
     ?s rdf:type dbo:PopulatedPlace. 
     ?s dbp:iso3166code ?code. 
     ?s dbo:populationTotal ?pop. 
     FILTER (?s = dbpedia:Switzerland) 
    }
"""
sparql.setQuery(query)
try:
    sparql.setReturnFormat(RDF)
    results = sparql.query()
    triples = results.convert()  # this converts directly to an RDFlib Graph object
except:
    print("query failed")


# add triples to graph
g += triples
