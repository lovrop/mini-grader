#!/usr/bin/env python3
import collections
import logging
import os
import re
import sys
import time

# These are always searched
EXAMPLE_PATTERNS = [
    # in1 out1
    (r'in(.+)', r'out(.+)'),
    # task.dummy.in.1 task.dummy.out.1
    (r'TASK.dummy.in(.+)', r'TASK.dummy.out(.+)'),
]

# These are omitted when --examples-only is used
FULL_PATTERNS = [
    # foo.in.1 foo.out.1 (new Croatian competitions)
    (r'TASK\.in\.(\d+[a-z]*)',
     r'TASK\.out\.(\d+[a-z]*)'),
    # foo.in1 foo.ou1 (old Croatian competitions)
    (r'TASK\.in([0-9a-z])',
     r'TASK\.ou([0-9a-z])'),
    # task_1.in task_1.out (IOI 2001)
    (r'TASK_(\d+)\.in',
     r'TASK_(\d+)\.out'),
    # 1.in 1.out (USACO)
    (r'(\d+)\.in',
     r'(\d+)\.out'),
    # task-001.in task-001.ans
    (r'TASK-(.+)\.in',
     r'TASK-(.+)\.ans'),
    # task.1.in task.1.out
    (r'TASK\.([0-9a-z]+)\.in',
     r'TASK\.([0-9a-z]+)\.out'),
    # C-large.{in,out} (Code Jam)
    (r'([a-z]-(?:small|large|practice).*)\.in',
     r'([a-z]-(?:small|large|practice).*)\.out'),
]


TestCase = collections.namedtuple('TestCase', ['task', 'dirpath', 'infile', 'outfile'])


def sort_filenames(l):
    """ Sort the given list in the way that humans expect.
        http://www.codinghorror.com/blog/2007/12/sorting-for-humans-natural-sort-order.html
    """
    import re
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda test_case: [ convert(c) for c in re.split('([0-9]+)', test_case.infile) ]
    l.sort(key=alphanum_key)


class TestDataSearch:
    def __init__(self,
                 search_dir,
                 is_example_run,
                 task,
                 executable):
        self.search_dir = search_dir
        self.is_example_run = is_example_run
        self.task = task
        self.executable = executable

    def search(self):
        patterns = EXAMPLE_PATTERNS + ([] if self.is_example_run else FULL_PATTERNS)
        logging.debug('patterns = %s', patterns)

        if self.task is None:
            # If task name is not specified on command line, try:
            # - the name of the current directory
            # - the name of the executable
            tasks_to_try = frozenset([
                os.path.basename(os.getcwd()),
                os.path.basename(os.path.splitext(self.executable)[0]),
                ])
        else:
            tasks_to_try = [self.task]
        logging.debug('tasks_to_try = %s', tasks_to_try)

        tests = {}
        for dirpath, _, filenames in os.walk(self.search_dir):
            for task in tasks_to_try:
                for pattern in patterns:
                    rv = self.search_one_pattern(dirpath, filenames, task, pattern)
                    logging.debug('pattern {}: {}'.format(pattern[0], rv))
                    # Some patterns do not depend on the task name so we might
                    # go through them more than once if we are trying different
                    # task names.  To deal with this, `tests' is a dict keyed
                    # by the input file, which will dedup.
                    for tc in rv:
                        tests[(tc.dirpath, tc.infile)] = tc
        tests = list(tests.values())
        if not tests:
            logging.error('No test data found!')
            sys.exit(1)
        logging.info('Found %d test cases', len(tests))
        sort_filenames(tests)
        return tests

    def search_one_pattern(self, dirpath, filenames, task, pattern):
        tests = []
        re_in = re.compile(pattern[0].replace('TASK', task) + '$')
        re_out = re.compile(pattern[1].replace('TASK', task) + '$')
        inputs = {}
        outputs = {}
        for filename in filenames:
            for regex, outdict in [(re_in, inputs), (re_out, outputs)]:
                m = regex.match(filename.lower())
                if m:
                    outdict[m.groups(1)] = filename
                    break
        for seq, infile in inputs.items():
            if seq in outputs:
                tests.append(TestCase(task=task,
                                      dirpath=dirpath,
                                      infile=infile,
                                      outfile=outputs[seq]))
        return tests
