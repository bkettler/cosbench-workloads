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
                --size SIZE --workers WORKERS --runtime RUNTIME --serverct
                SERVERCT --servermem SERVERMEM [--buckets BUCKETS]
                [--cachewrkrs CACHEWRKRS] [--cleanwrkrs CLEANWRKRS]
                [--prepwrkrs PREPWRKRS]

Generate COSBench workloads.

optional arguments:
  -h, --help            show this help message and exit
  --s3url S3URL         S3 endpoint URL
  --s3access S3ACCESS   S3 access key
  --s3secret S3SECRET   S3 secret key
  --size SIZE           Object size in KB
  --workers WORKERS     worker count
  --runtime RUNTIME     run time in seconds
  --serverct SERVERCT   the number of RING servers
  --servermem SERVERMEM
                        RAM per server in GB
  --buckets BUCKETS     bucket count, default 1
  --cachewrkrs CACHEWRKRS
                        worker count for clearcache stages, default 300
  --cleanwrkrs CLEANWRKRS
                        worker count for cleanup stages, default 300
  --prepwrkrs PREPWRKRS
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

# Examples

In the following example we have a RING with 6 servers and each server has 128 GB of RAM. We are executing tests for objects sizes 512KB, 1MB, 10MB, 100MB, and 1GB as well as 10, 50 and 300 workers.

```
$ export COSBENCH_PATH=/root/cosbench
$ ./setup.py \
--s3url http://s3.scality.lab/ \
--s3access 1EHMEV1FR7UOF8YF1SEA \
--s3secret uCuPZzFO4E9uejapOq7TDEW8xwygXKzwA/ZwTtDI \
--size 512 \
--size 1024 \
--size 10240 \
--size 102400 \
--size 1048576 \
--workers 10 \
--workers 50 \
--workers 300 \
--runtime 300 \
--serverct 6 \
--servermem 128
Generated workloads/512_kb_1_buckets_10_workers.xml
Generated workloads/512_kb_1_buckets_50_workers.xml
Generated workloads/512_kb_1_buckets_300_workers.xml
Generated workloads/1024_kb_1_buckets_10_workers.xml
Generated workloads/1024_kb_1_buckets_50_workers.xml
Generated workloads/1024_kb_1_buckets_300_workers.xml
Generated workloads/10240_kb_1_buckets_10_workers.xml
Generated workloads/10240_kb_1_buckets_50_workers.xml
Generated workloads/10240_kb_1_buckets_300_workers.xml
Generated workloads/102400_kb_1_buckets_10_workers.xml
Generated workloads/102400_kb_1_buckets_50_workers.xml
Generated workloads/102400_kb_1_buckets_300_workers.xml
Generated workloads/1048576_kb_1_buckets_10_workers.xml
Generated workloads/1048576_kb_1_buckets_50_workers.xml
Generated workloads/1048576_kb_1_buckets_300_workers.xml
$ ./run.sh
Accepted with ID: w1
Accepted with ID: w2
Accepted with ID: w3
Accepted with ID: w4
Accepted with ID: w5
Accepted with ID: w6
Accepted with ID: w7
Accepted with ID: w8
Accepted with ID: w9
Accepted with ID: w10
Accepted with ID: w11
Accepted with ID: w12
Accepted with ID: w13
Accepted with ID: w14
Accepted with ID: w15
```
