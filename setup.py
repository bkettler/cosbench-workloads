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
    parser.add_argument('--sizes', dest='sizes', type=str, required=True,
                        help='a comma seperated list of objects sizes in KB')
    parser.add_argument('--buckets', dest='buckets', type=int, required=False,
                        default=1, help='bucket count')
    parser.add_argument('--workers', dest='workers', type=int, required=True,
                        help='worker count')
    parser.add_argument('--runtime', dest='runtime', type=int, required=True,
                        help='run time in seconds')
    parser.add_argument('--server-ct', dest='server_ct', type=int,
                        required=True, help='the number of RING servers')
    parser.add_argument('--server-mem', dest='server_mem', type=int,
                        required=True, help='RAM per server in GB')
    args = parser.parse_args()

    # A little error checking
    try:
        sizes = [int(s) for s in args.sizes.split(',')]
    except ValueError as e:
        print 'Invalid size'
        print e
        sys.exit(1)

    # Create the output dir
    output_d = 'workloads'
    if not os.path.exists(output_d):
        os.mkdir(output_d)

    # Read the template file
    with open('template.xml', 'r') as fh:
        workload = fh.read()

    """
    Here we will calculate the total ops for the clearcache stage. In order to
    reduce caching effects we will write roughly 2x total memory. The
    clearcache workstage uses 300 workers and an object size of 100MB. We will
    use base 10 instead of base 2 because it makes maths simpler.
    """
    totalmem_mb = args.server_ct * args.server_mem * 1000
    cacheops = 2 * totalmem_mb / 100
    # The totalOps must be a factor of workers so maths
    quotient, remainder = divmod(cacheops, 300)
    if remainder:
        cacheops = (quotient + 1) * 300

    # Build the workload files for each defined size
    for size in sizes:
        new_workload = workload.replace('_SIZE_', str(size))
        new_workload = new_workload.replace('_S3URL_', str(args.s3url))
        new_workload = new_workload.replace('_SECRETKEY_', str(args.s3secret))
        new_workload = new_workload.replace('_ACCESSKEY_', str(args.s3access))
        new_workload = new_workload.replace('_BUCKETS_', str(args.buckets))
        new_workload = new_workload.replace('_WORKERS_', str(args.workers))
        new_workload = new_workload.replace('_RUNTIME_', str(args.runtime))
        new_workload = new_workload.replace('_CACHE_', str(cacheops))

        """
        Here we will calculate the object count for all normal stages. In order
        to reduce caching effects we will use an object division strategy in
        all normal stages and an object count roughly equivalent to 2x total
        memory. We will use base 10 instead of base 2 because it makes maths
        simpler.
        """
        totalmem_kb = args.server_ct * args.server_mem * 1000**2
        objects = 2*totalmem_kb / float(size)
        # Make objects a factor of workers so the division strategy is clean
        quotient, remainder = divmod(objects, args.workers)
        if remainder:
            objects = (quotient + 1) * args.workers
        new_workload = new_workload.replace('_OBJECTS_', str(int(objects)))

        output_f = '%s.xml' % '_'.join([str(size), 'kb', str(args.buckets),
                                        'buckets', str(args.workers),
                                        'workers'])
        output = os.path.join(output_d, output_f)
        with open(output, 'w') as fh:
            fh.write(new_workload)
        print "Generated %s" % output
