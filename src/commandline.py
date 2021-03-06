#!/usr/bin/env python3

import argparse
import multiprocessing
import re
import sys

from . import platform_dependent

DESCRIPTION = (
    'Mini grader for programming competition tasks, especially for contests with downloadable ' +
    'test data (but no online grader).'
    )

def parse():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('executable',
                        help='path to executable')

    parser.add_argument('-D', '--test-data-dir',
                        metavar='DIR',
                        help='full run, with test data in specified directory')
    parser.add_argument('-m', '--memory-limit',
                        action=StoreMemoryLimitAction,
                        default=2**30,
                        metavar='MEM',
                        help="memory limit e.g. '256M' or '0.25G' (default is 1G)")
    parser.add_argument('-t', '--time-limit',
                        default=sys.maxsize,
                        metavar='SECONDS',
                        type=float,
                        help='time limit in seconds (default is unlimited)')

    parser.add_argument('-x', '--examples-only',
                        dest='example_run',
                        action='store_true',
                        help='consider only example filename patterns for test data')
    parser.add_argument('--task',
                        help='task name, used to search for test data (default is to infer from ' +
                             'executable name and/or current directory)')
    parser.add_argument('-j', '--threads',
                        dest='nthreads',
                        default=platform_dependent.cpu_count(),
                        type=int,
                        help='run this many test cases in parallel (default is CPU count)')
    parser.add_argument('--usaco',
                        dest='usaco_style_io',
                        action='store_true',
                        help='USACO-style input/output, through files named TASK.in and TASK.out')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='output informational messages')
    parser.add_argument('-w', '--ignore-space',
                        action='store_true',
                        help='ignore trailing spaces and empty lines when checking output')
    parser.add_argument('--color',
                        default='auto',
                        choices=['auto', 'always', 'none'],
                        help='colored output')
    args = parser.parse_args()
    return args

class StoreMemoryLimitAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        match = re.match(r'([0-9]+(?:\.[0-9]+)?)([GgMm])[Bb]?', values)
        if not match:
            raise argparse.ArgumentError(self, "invalid memory limit: '%s'" % values)

        num = float(match.group(1))
        suffix = match.group(2)
        if suffix.lower() == 'g':
            num *= 2**30
        elif suffix.lower() == 'm':
            num *= 2**20
        setattr(namespace, self.dest, num)
