A collection of COSBench workloads.

# Usage

The path to your COSBench installation must be define with the COSBENCH_PATH environment variable.

e.g.
```
$ export COSBENCH_PATH=/root/cosbench
```

Use the setup.py script to generate environment specific workload definitions including your S3 endpoint, secret key, access key, workers as well as calculate the parameters needed for the [clearcache](#caching) workstage.

```
$ ./setup.py --help
usage: setup.py [-h] --s3url S3URL --s3access S3ACCESS --s3secret S3SECRET
                --sizes SIZES --objects OBJECTS --buckets BUCKETS --workers
                WORKERS --runtime RUNTIME --cachesz CACHESZ

Generate COSBench workloads.

optional arguments:
  -h, --help           show this help message and exit
  --s3url S3URL        S3 endpoint URL
  --s3access S3ACCESS  S3 access key
  --s3secret S3SECRET  S3 secret key
  --sizes SIZES        a comma seperated list of objects sizes in KB
  --objects OBJECTS    object count
  --buckets BUCKETS    bucket count
  --workers WORKERS    worker count
  --runtime RUNTIME    run time in seconds
  --cachesz CACHESZ    the size in KB for the cache workstage
```

Once your workload definitions are generated the run.sh script will generate a hash value unique for each run and submit the workloads.

```
$ ./run.sh
```

# Considerations

## Reads

There are two concerns that need to be addressed when performing read workloads: data locality and caching.

### Caching

In order to avoid inflated results as a result of cached data a special workload called 'clearcache' is executed in between each read test. The clearcache workload executes a series of writes roughly equivalent to 2x the total RING memory capacity. As an example if the RING is comprised of 6 servers with 128GB of RAM per server the clearcache workload will write 6 * 128 * 2 GB of data.

### Data Locality

When objects are written sequentially the probablility that the chunks end up in the same .dat file on disk or more generally around the same physical location on the drive platter is high. If data is read in the same order it is written the workload can benefit from the locality of the bits on disk and cause artifically inflated results. In order to avoid inflated results as a result of locality on disk the object count per workload is kept high and the uniform selector is used for both the bucket and object selection so that the access patter is randomized (see the Selector section in the COSBench user guide).

## Writes

Deletes on the RING are asychronous meaning workloads that are run more than once may actually be overwriting existing objects vs writing new objects. In order to avoid overwriting existing objects each time a workloads is submitted a unique object prefix is used. A random 32 character hash is generated for each workload automagically by the run.sh script.

```
head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32
```

The random string is substitued for HASH in the oprefix string.

e.g.
```
<work name="2575rw" workers="1" runtime="1800">
  <operation type="read" ratio="25" config="cprefix=1mb-bob;containers=u(1,1);oprefix=r-HASH;objects=u(1,1280000)" />
  <operation type="write" ratio="75" config="cprefix=1mb-bob;containers=u(1,1);oprefix=w3-HASH;objects=s(1,1280000);sizes=c(1)MB" />
</work>
```
