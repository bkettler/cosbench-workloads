#!/usr/bin/python
#
# Generate a series of COSBench workload files based on provided arguments.
#

import sys
import os
import math
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
    #parser.add_argument('--objects', dest='objects', type=int, required=True,
    #                    help='object count')
    parser.add_argument('--buckets', dest='buckets', type=int, required=False,
                        default=1, help='bucket count')
    parser.add_argument('--workers', dest='workers', type=int, required=True,
                        help='worker count')
    parser.add_argument('--runtime', dest='runtime', type=int, required=True,
                        help='run time in seconds')
    parser.add_argument('--cachesz', dest='cachesz', type=int,
                        required=True,
                        help='the size in KB for the cache workstage')
    args = parser.parse_args()

    # A little error checking
    try:
        sizes = [int(s) for s in args.sizes.split(',')]
    except ValueError as e:
        print 'Invalid size'
        print e
        sys.exit(1)

    # Output dir
    output_d = 'workloads'
    if not os.path.exists(output_d):
        os.mkdir(output_d)

    with open('template.xml', 'r') as fh:
        workload = fh.read()

    for size in sizes:
        new_workload = workload.replace('_SIZE_', str(size))
        new_workload = new_workload.replace('_S3URL_', str(args.s3url))
        new_workload = new_workload.replace('_SECRETKEY_', str(args.s3secret))
        new_workload = new_workload.replace('_ACCESSKEY_', str(args.s3access))
        #new_workload = new_workload.replace('_OBJECTS_', str(args.objects))
        new_workload = new_workload.replace('_BUCKETS_', str(args.buckets))
        new_workload = new_workload.replace('_WORKERS_', str(args.workers))
        new_workload = new_workload.replace('_RUNTIME_', str(args.runtime))

        # We will use an object count roughly equivalent to 2*cachesz/size,
        # but it must be a multiple of workers
        objects = int(math.ceil(float(args.cachesz)*2/size/args.workers)) * \
                  args.workers
        new_workload = new_workload.replace('_OBJECTS_', str(objects))

        # The clearcache workstage uses 100M objects so maths
        cachesz = int(math.ceil(float(args.cachesz)*2/1000/100))
        new_workload = new_workload.replace('_CACHE_', str(cachesz))

        output_f = '%s.xml' % '_'.join([str(size), 'kb', str(args.buckets),
                                      'buckets', str(args.workers), 'workers'])
        output = os.path.join(output_d, output_f)
        with open(output, 'w') as fh:
            fh.write(new_workload)
        print "Generated workload '%s'" % output
