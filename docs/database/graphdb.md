# GraphDB

## What is GraphDB?

TODO

## Prerequisites

As a reference, the following are the recommended minimum hardware requirements to run 
the LUBM Benchmark for 1000 universities on GraphDB 9.10.0 and above.

| Prerequisites |                                                                                      |
|---------------|--------------------------------------------------------------------------------------|
| CPU           | 2.7 GHz 4-Core Intel Core i7                                                         |
| Disk Space    | `80 GB` of free disk space is required for the test dataset download and triplestore |
| Memory        | `32 GB` of RAM is required for the GraphDB server to run                             |

Also check the [GraphDB System Requirements](https://graphdb.ontotext.com/documentation/standard/requirements.html).

## Installing GraphDB

Download the GraphDB Enterprise Edition [60-day trial](https://www.ontotext.com/products/graphdb/graphdb-enterprise/). 
This is the most scalable and resilient version of GraphDB.

Unzip its contents to a local folder of your preference.
Note that this location will be used to set the value of the parameter `-d` (distribution directory) 
in the next section.

Check the prerequisites in the GraphDB README file. You may need to install a different version of Java.

## Executing the Benchmark

The Benchmark for GraphDB is fully automated.

Run the `graphdb-execute-benchmark.sh` script, as per example below:

```
./graphdb-execute-benchmark.sh \
    -m "Xms2460m" -x "Xmx7400m" \
    -i preload -d ~/Triplestores/Downloads/graphdb-ee-9.10.0 \
    -s ~/Triplestores/Servers/GraphDB-9.10.0 \
    -u 1000 -f ntriple -t 1800 -c full \
    -p zip
```

Usage:

```
./graphdb-execute-benchmark.sh \
    -m <min-heap-size> -x <max-heap-size> \
    -i <data-load-interface> -d <graphdb-download> \
    -s <graphdb-server> \
    -u <universities> -f <file-format> -t <query-timeout> -c <test-coverage> \
    -p <file-compression>
```

```
-m min Java heap (min)
-x max Java heap (opt)
-i data import method; values are preload or loadrdf.
-d location of the GraphDB download (distribution directory)
-s location where the GraphDB server will run and database files be stored.
-u number of universities
-f file format (ntriple or turtle)
-t query timeout in seconds
-c test coverage (loadonly or full). Loadonly will only import the test dataset whereas Full will also execute the sparql queries.
-p file compression (zip, gzip or none)
```

Recommended values for the GraphDB memory usage, parameter `-m`, 
can be found [here](https://graphdb.ontotext.com/documentation/standard/requirements.html).

> *_NOTE_*: It is not recommended executing any memory-intensive applications while the benchmark is running.

## Analysing Test Results

Data import, optimisation, and query timings will be logged to the `Results/Query-Timings/graphdb-import-optmise-query-timings.log` file and the query outputs to the appropriate files in the `Results/Query-Results` folder.

The logs are cleaned in the beginning of each run.

## Environment Clean up

In the end of the benchmark execution, there is a clean-up task that removes the triplestore server, 
its databases and data files.
The test result logs are kept for analysis, but cleaned in the beginning of each execution.
The product download is not deleted.

--8<-- "abbreviations.md"
