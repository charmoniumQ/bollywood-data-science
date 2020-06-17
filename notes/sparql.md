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
SELECT DISTINCT ?person WHERE {
  ?person wdt:P106 wd:Q33999 .
  {
          { ?person wdt:P27 wd:Q668 . }
    UNION { ?person wdt:P19/wdt:? wd:Q668 . }
  } .
}
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
