A collection of COSBench workloads.

# Usage

The path to your COSBench installation must be defined with the COSBENCH_PATH environment variable.

e.g.
```
$ export COSBENCH_PATH=/root/cosbench
```

Use the setup.py script to generate environment specific workload definitions including your S3 endpoint, secret key, access key, workers as well as calculate the parameters needed for the [clearcache](#caching) workstage.

```
$ ./setup.py --help
usage: setup.py [-h] --s3url S3URL --s3access S3ACCESS --s3secret S3SECRET
                --sizes SIZES --workers WORKERS --runtime RUNTIME --serverct
                SERVERCT --servermem SERVERMEM [--buckets BUCKETS]
                [--cachewrkrs CACHEWRKRS] [--cleanupwrkrs CLEANUPWRKRS]
                [--preparewrkrs PREPAREWRKRS]

Generate COSBench workloads.

optional arguments:
  -h, --help            show this help message and exit
  --s3url S3URL         S3 endpoint URL
  --s3access S3ACCESS   S3 access key
  --s3secret S3SECRET   S3 secret key
  --sizes SIZES         a comma seperated list of objects sizes in KB
  --workers WORKERS     worker count
  --runtime RUNTIME     run time in seconds
  --serverct SERVERCT   the number of RING servers
  --servermem SERVERMEM
                        RAM per server in GB
  --buckets BUCKETS     bucket count, default 1
  --cachewrkrs CACHEWRKRS
                        worker count for clearcache stages, default 300
  --cleanupwrkrs CLEANUPWRKRS
                        worker count for cleanup stages, default 300
  --preparewrkrs PREPAREWRKRS
                        worker count for prepare stages, default 300
```

Once your workload definitions are generated the run.sh script will generate a [hash](#writes) value unique for each run and submit the workloads.

```
$ ./run.sh
```

# Considerations

## Reads

There are two concerns that need to be addressed when performing read workloads: data locality and caching.

### Caching

In order to avoid inflated results as a result of data caching we are using three different strategies.

1. A special work stage called 'clearcache' is executed in between each read test. The clearcache workload executes a series of writes roughly equivalent to 2x the total RING memory capacity. As an example if the RING is comprised of 6 servers with 128GB of RAM per server the clearcache workload will write 6 * 128 * 2 = 1536GB of data.
2. The working set for all read stages is roughly equivalent to 2x the total RING memory capacity. By using a working set that is 2x the total RING memory we attempt to keep our object counts high enough and our working set large enough that it can't fit entirely in memory.
3. We also use an object division strategy for all normal stages which partitions the work by object. This division strategy ensures each worker operates on it's own range of objects to prevent two workers from reading the same object at the same time. 

### Data Locality

When objects are written sequentially the probablility that the chunks end up in the same .dat file on disk or more generally around the same physical location on the drive platter is high. If data is read in the same order it is written the workload can benefit from the locality of the bits on disk and cause artifically inflated results. In order to avoid inflated results as a result of locality on disk the object count per workload is kept high and the uniform selector is used for both the bucket and object selection so that the access patter is randomized (see the Selector section in the COSBench user guide).

## Writes

Deletes on the RING are asychronous meaning workloads that are run more than once may actually be overwriting existing objects vs writing new objects. In order to avoid overwriting existing objects each time a workloads is submitted a unique object prefix is used. A random 32 character hash is generated for each workload automagically by the run.sh script.

