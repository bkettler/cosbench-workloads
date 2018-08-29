#!/usr/bin/python
#
# Generate a series of COSBench workload files based on provided arguments.
#

import sys
import os
from argparse import ArgumentParser

if __name__ == '__main__':
    # Define CLI arguments.
    parser = ArgumentParser(description='Generate COSBench workloads.')
    parser.add_argument('--s3url', dest='s3url', type=str, required=True,
                        help='S3 endpoint URL')
    parser.add_argument('--s3access', dest='s3access', type=str, required=True,
                        help='S3 access key')
    parser.add_argument('--s3secret', dest='s3secret', type=str, required=True,
                        help='S3 secret key')
    parser.add_argument('--size', dest='size', type=int, required=True,
                        action='append', help='Object size in KB')
    parser.add_argument('--workers', dest='workers', type=int, required=True,
                        action='append', help='worker count')
    parser.add_argument('--runtime', dest='runtime', type=int, required=True,
                        help='run time in seconds')
    parser.add_argument('--serverct', dest='serverct', type=int,
                        required=True, help='the number of RING servers')
    parser.add_argument('--servermem', dest='servermem', type=int,
                        required=True, help='RAM per server in GB')
    parser.add_argument('--buckets', dest='buckets', type=int, required=False,
                        default=1, help='bucket count, default 1')
    parser.add_argument('--cachewrkrs', dest='cachewrkrs', type=int,
                        required=False, default=300,
                        help='worker count for clearcache stages, default 300')
    parser.add_argument('--cleanwrkrs', dest='cleanwrkrs', type=int,
                        required=False, default=300,
                        help='worker count for cleanup stages, default 300')
    parser.add_argument('--prepwrkrs', dest='prepwrkrs', type=int,
                        required=False, default=300,
                        help='worker count for prepare stages, default 300')
    args = parser.parse_args()

    # Create the output dir
    output_d = 'workloads'
    if not os.path.exists(output_d):
        os.mkdir(output_d)

    # Read the template file
    with open('template.xml', 'r') as fh:
        wload_template = fh.read()

    """
    Here we will calculate the total ops for the clearcache stage. In order to
    reduce caching effects we will write roughly 2x total memory. The
    clearcache workstage uses 300 workers and an object size of 100MB. We will
    use base 10 instead of base 2 because it makes maths simpler.
    """
    totalmem_mb = args.serverct * args.servermem * 1000
    cacheops = 2 * totalmem_mb / 100
    # The totalOps must be a factor of workers so maths
    quotient, remainder = divmod(cacheops, 300)
    if remainder:
        cacheops = (quotient + 1) * 300

    # Build the workload files for each defined size
    for size in args.size:
        for workers in args.workers:
            new_wload = wload_template.replace('_SIZE_', str(size))
            new_wload = new_wload.replace('_S3URL_', str(args.s3url))
            new_wload = new_wload.replace('_SECRETKEY_', str(args.s3secret))
            new_wload = new_wload.replace('_ACCESSKEY_', str(args.s3access))
            new_wload = new_wload.replace('_BUCKETS_', str(args.buckets))
            new_wload = new_wload.replace('_WORKERS_', str(workers))
            new_wload = new_wload.replace('_RUNTIME_', str(args.runtime))
            new_wload = new_wload.replace('_CACHE_', str(cacheops))
            new_wload = new_wload.replace('_PREPWRKRS_', str(args.prepwrkrs))
            new_wload = new_wload.replace('_CACHEWRKRS_', str(args.cachewrkrs))
            new_wload = new_wload.replace('_CLEANWRKRS_', str(args.cleanwrkrs))

            """
            Here we will calculate the object count for all normal stages. In
            order to reduce caching effects we use an object count roughly
            equivalent to 2x total memory. An object division strategy is also
            being used so the count should be a factor of workers. We will use
            base 10 instead of base 2 because it makes maths simpler.
            """
            totalmem_kb = args.serverct * args.servermem * 1000**2
            objects = 2*totalmem_kb / float(size)
            # Make objects a factor of workers so division strategy is clean
            quotient, remainder = divmod(objects, workers)
            if remainder:
                objects = (quotient + 1) * workers
            new_wload = new_wload.replace('_OBJECTS_', str(int(objects)))

            # Write the workload xml
            output_f = '%s.xml' % '_'.join([str(size), 'kb', str(args.buckets),
                                            'buckets', str(workers),
                                            'workers'])
            output = os.path.join(output_d, output_f)
            with open(output, 'w') as fh:
                fh.write(new_wload)
            print "Generated %s" % output
