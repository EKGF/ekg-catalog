# SPARQL

SPARQL (pronounced "sparkle" /ˈspɑːkəl/, a recursive acronym for SPARQL Protocol and RDF Query Language) is an RDF query language—that is, a semantic query language for databases—able to retrieve and manipulate data stored in Resource Description Framework (RDF) format.


```sparql
PREFIX lcc-cr: <https://www.omg.org/spec/LCC/Countries/CountryRepresentation/>

SELECT DISTINCT
    ?graph
    ?region
    ?regionLabel
WHERE {
    GRAPH ?graph {
        ?region a lcc-cr:Country .
        ?region ?p ?regionObject .
        ?region rdfs:label ?regionLabel .

        BIND(COALESCE(?searchText, "") AS ?searchTextBound)

        FILTER (
            CONTAINS(LCASE(?regionObject), LCASE(?searchTextBound))
        )
    }
}
ORDER BY ?regionLabel
```
