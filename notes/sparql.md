[DBPedia](http://dbpedia.org/snorql/)

```
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT DISTINCT ?person WHERE {
  {
          { ?person a dbo:Actor . }
    UNION { ?person a umbel-rc:Actor . }
  } .
  {
          { ?person dbo:country dbr:India . }
    UNION { ?person dbo:birthPlace/dbo:country? dbr:India . }
    UNION { ?person dbo:nationality dbr:India , dbr:Indian_people . }
    UNION { ?person dbo:stateOfOrigin dbr:India . }
  } .
}
```


[WikiData](https://query.wikidata.org/)

```
      PREFIX wd: <http://www.wikidata.org/entity/>
      PREFIX wdt: <http://www.wikidata.org/prop/direct/>
      PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
      CONSTRUCT {
        ?person rdf:label ?personLabel .
        ?person wdt:P345 ?personImd .
        ?person wdt:P569 ?dob .
        ?person wdt:P19 ?pob .
        ?person wdt:P22 ?father .
        ?person wdt:P25 ?mother .
      } WHERE {
        ?person wdt:P106 wd:Q33999 .
        {
          { ?person wdt:P27 wd:Q668 . } UNION
          { ?person wdt:P19/wdt:? wd:Q668 . } .
        } .
        OPTIONAL { ?person wdt:P345 ?imdb . } .
		OPTIONAL { ?person wdt:P569 ?dob . } .
		OPTIONAL { ?person wdt:P19 ?pob . } .
		OPTIONAL { ?person wdt:P22 ?father . } .
		OPTIONAL { ?person wdt:P25 ?mother . } .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . } .
      } LIMIT 1000
```

[YAGO3](https://yago-knowledge.org/sparql)

```
PREFIX yago: <http://yago-knowledge.org/resource/>
PREFIX schema: <http://schema.org/>
SELECT DISTINCT ?person WHERE {
  ?person schema:hasOccupation yago:film_actor_Q10800557 .
  {
          { ?person schema:birthPlace/schema:containedInPlace* yago:India . }
    UNION { ?person schema:nationality yago:India . }
  } .
} 
```
