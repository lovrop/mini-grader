# See README for documentation.  Run with --help to get detailed usage information.

import concurrent.futures
import logging
import multiprocessing
import os
import re
import sys
import time

from . import checkers
from . import commandline
from .clint.textui import colored
from .scoreboard import Scoreboard
from .runner import Runner
from .test_data_search import TestDataSearch

def main():
    args = commandline.parse()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if args.color != 'auto':
        colored.setColorEnabled(args.color == 'always')

    # Look for test data
    test_data_search_dir = args.test_data_dir
    if test_data_search_dir is None:
        test_data_search_dir = '.'
    tests = TestDataSearch(test_data_search_dir,
                           args.example_run,
                           args.task,
                           args.executable).search()

    logging.info('Running %d test cases in parallel', args.nthreads)
    executor = concurrent.futures.ThreadPoolExecutor(args.nthreads)
    scoreboard = Scoreboard()
    runners = []
    futures = []

    for test_case in tests:
        infilepath = os.path.join(test_case.dirpath, test_case.infile)
        outfilepath = os.path.join(test_case.dirpath, test_case.outfile)
        runner = Runner(test_case.task,
                        args.executable,
                        infilepath,
                        outfilepath,
                        checkers.Checker(),
                        args.usaco_style_io)
        future = executor.submit(runner.run, args.time_limit, args.memory_limit)
        scoreboard.add(test_case.infile, runner, future)
        runners.append(runner)

    code = scoreboard.start()
    executor.shutdown()
    sys.exit(code)
