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
from .scoreboard import Scoreboard
from .runner import Runner
from .test_data_search import TestDataSearch

def main():
    args = commandline.parse()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Look for test data
    test_data_search_dir = args.test_data_dir
    if test_data_search_dir is None:
        test_data_search_dir = '.'
    search_result = TestDataSearch(test_data_search_dir,
                                   args.example_run,
                                   args.task,
                                   args.executable).search()

    logging.info('Running %d test cases in parallel', args.nthreads)
    executor = concurrent.futures.ThreadPoolExecutor(args.nthreads)
    scoreboard = Scoreboard()
    futures = []

    for iname, oname in search_result.tests:
        infilepath = os.path.join(search_result.dirpath, iname)
        outfilepath = os.path.join(search_result.dirpath, oname)
        checker = checkers.DiffChecker()
        runner = Runner(search_result.task,
                        args.executable,
                        infilepath,
                        outfilepath,
                        checker,
                        args.usaco_style_io)
        future = executor.submit(runner.run, args.time_limit, args.memory_limit)
        scoreboard.add(iname, runner, future)

    scoreboard.start()
    executor.shutdown()
