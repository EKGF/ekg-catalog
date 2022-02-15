# Stardog Enterprise Knowledge Graph Platform

## What is Stardog?

From the [Stardog website](https://www.stardog.com/platform):

> [Stardog Enterprise Knowledge Graph Platform](https://www.stardog.com/platform/):
> 
> Create a flexible, reusable data layer for answering complex queries across 
> data silos. Stardog unifies data based on its meaning, creating a 
> connected network of knowledge to power your business.

TODO

## Benchmark

### Prerequisites

As a reference, the following are the recommended minimum hardware requirements to run
the LUBM Benchmark for 1000 universities on Stardog 7.7.2 and above.

| Prerequisites |                                                                                      |
|---------------|--------------------------------------------------------------------------------------|
| CPU           | 2.7 GHz 4-Core Intel Core i7                                                         |
| Disk Space    | `80 GB` of free disk space is required for the test dataset download and triplestore |
| Memory        | `32 GB` of RAM is required for the GraphDB server to run                             |

Also check the [Stardog System Requirements](https://docs.stardog.com/get-started/install-stardog/system-requirements).

### Installing Stardog

```
brew install stardog-union/tap/stardog
```

Homebrew will take care of the installation for you including adding Stardog’s `/bin` folder to 
your PATH so `stardog` and `stardog-admin` commands can be used regardless of current working directory.

If you come across issues when installing or running Stardog on a MacOS, please try the [Manual Installation](https://docs.stardog.com/get-started/install-stardog/macOS-installation#manual-installation).


### Executing the Benchmark

The Benchmark for Stardog is fully automated.

Run the `stardog-execute-benchmark` command located at the root of the branch, as per example below.

```
./stardog-execute-benchmark.sh \
    -m "-Xmx8g -Xms8g -XX:MaxDirectMemorySize=20g" \
    -s ~/Triplestores/Servers/Stardog-7.7.2 \
    -u 1000 -f ntriple -t 30m -c full \
    -p gzip
```
Usage:

```
./stardog-execute-benchmark.sh \
    -m <java-mem-args> \ 
    -s <stardog-home> \
    -u <universities> -f <file-format> -t <query-timeout> -c <test-coverage> \
    -p <file-compression>
```

```
-m stardog memory usage
-s location where Stardog server will run and database files be stored.
-u number of universities
-f file format (ntriple or turtle)
-t query timeout (e.g. 1800s, 30m, 2h)
-c test coverage (loadonly or full). Loadonly will only import the test dataset whereas Full will also execute the sparql queries.
-p file compression (zip, gzip, bz2 or none)
```

Recommended values for the Stardog memory usage, parameter `-m`, can be found [here](https://docs.stardog.com/operating-stardog/server-administration/capacity-planning#memory-usage).

The location specified in `-s` gets created for you automatically.
You may probably choose to use the suggested location provided by the example.

> *_NOTE_*: It is not recommended executing any memory-intensive applications while the benchmark is running.

### Analysing Test Results

Query timings will be logged to the `Results/Query-Timings/slow_query.log` file and the  query outputs to the 
appropriate files in the `Results/Query-Results` folder. 
The data import and optimise timings will be logged to the `Results/Query-Timings/stardog-import-and-optmise-timings.log`

The logs are cleaned in the beginning of each run.

### Environment Clean up

In the end of the benchmark execution, there is a clean up task that removes the triplestore server, 
its databases and data files. 
The test result logs are kept for analysis, but cleaned in the beginning of each execution. 
The product download is not deleted.


--8<-- "abbreviations.md"
