# Oxford Semantic Technologies - RDFox

## What is RDFox?

RDFox provides the following main functionality:

- RDFox can import RDF triples, rules, and OWL 2 and SWRL axioms either 
  programmatically or from files of certain formats.
  RDF data can be validated using the SHACL constraint language.
  Additionally, RDFox can access information from external data sources, 
  such as CSV files, relational databases, or Apache Solr.
- Triples, rules and axioms can be exported into a number of different formats.
  Furthermore, the contents of the system can be incrementally saved into a 
  binary file, which can later be loaded to restore the system’s state.
- RDFox supports ACID transactional updates.
- Individual information elements in the system can be assigned different 
  access permissions for different users.
- RDFox can answer SPARQL 1.1 queries and provides functionality for 
  monitoring query answering and accessing query plans.
- RDFox supports materialization-based reasoning, where all triples that 
  logically follow from the facts and rules in the system are materialized
  as new triples.
  Materializations can be incrementally updated, which means that reasoning
  does not need to be performed from scratch once the information in the 
  system is updated.
  Furthermore, the results of reasoning can be explained, which means 
  that RDFox is able to return proofs for any new fact added to the store 
  through materialization.

## Prerequisites

As a reference, the following are the recommended minimum hardware 
requirements to run the LUBM Benchmark for 1000 universities on
RDFox 5.4 and above.

| Prerequisites |                                                                                      |
|---------------|--------------------------------------------------------------------------------------|
| CPU           | 2.7 GHz 4-Core Intel Core i7                                                         |
| Disk Space    | `80 GB` of free disk space is required for the test dataset download and triplestore |
| Memory        | `32 GB` of RAM is required for the RDFox server to run                               |

## Installing RDFox

Download the latest version of RDFox from their
[web site](https://www.oxfordsemantic.tech/downloads).

Unzip its contents to a local folder of your preference. 
Note that this location will be used to set the value of the 
parameter `-d` in the next section.


## Executing the Benchmark

The Benchmark for RDFox is fully automated.

Run the `rdfox-execute-benchmark` command located at the root of the 
branch, as per example below.

```
./rdfox-execute-benchmark.sh \
    -d ~/Triplestores/Downloads/RDFox-macOS-x86_64-5.4 \
    -s ~/Triplestores/Servers/RDFox-5.4 \
    -u 1000 -f ntriple -c full -p gzip
```

Usage:

```
./rdfox-execute-benchmark.sh \
    -d <rdfox-download> \
    -s <rdfox-server> \
    -u <universities> -f <file-format> -c <test-coverage> \
    -p <file-compression>
```

```
-d local folder where RDFox download was unzipped to.
-s location where RDFox server will run and data store files be stored.
-u number of universities
-f file format (ntriple or turtle)
-c test coverage (loadonly or full). Loadonly will only import the test dataset whereas Full will also execute the sparql queries.
-p file compression (zip, gzip, bz2 or none)
```

The location specified in `-s` gets created for you automatically. You may probably choose to use the suggested location provided by the example.

> *_NOTE_*: You may be prompted to allow RDFox to accept incoming network connections and/or to allow the 
> application to run on MacOS for the first time. 
> This can be set in `System Preferences/Security & Privacy/Allow Apps Downloaded From`.

## Analysing Test Results

Data import and query timings and answer counts will be logged to 
the `Results/Query-Timings/rdfox-import-and-query-timings-and-counts.log` 
file and the query outputs to the appropriate files in 
the `Results/Query-Results` folder.

The logs are cleaned in the beginning of each run.

## Environment Clean up

In the end of the benchmark execution, there is a cleanup task that removes 
the triplestore server, its databases and data files. 
The test result logs are kept for analysis, but cleaned in the beginning 
of each execution. 
The product download is not deleted.


--8<-- "abbreviations.md"
