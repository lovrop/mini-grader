#!/usr/bin/env python3

import logging, os, re, sys, time

# Patterns that are matched for all runs
FULL_PATTERNS = [
    # foo.in.1 foo.out.1 (new Croatian competitions)
    (r'TASK\.in\.(\d+[a-z]*)', r'TASK\.out\.(\d+[a-z]*)'),
    # foo.in1 foo.ou1 (old Croatian competitions)
    (r'TASK\.in([0-9a-z])', r'TASK\.ou([0-9a-z])'),
    # task_1.in task_1.out (IOI 2001)
    (r'TASK_(\d+)\.in', r'TASK_(\d+)\.out'),
    # 1.in 1.out (USACO)
    (r'(\d+)\.in', r'(\d+)\.out'),
    # task-001.in task-001.ans
    (r'TASK-(.+)\.in', r'TASK-(.+)\.ans'),
    ]

# Patterns that are matched even when --examples-only is used
EXAMPLE_PATTERNS = [
    # in1 out1
    (r'in(.+)', r'out(.+)'),
    # task.dummy.in.1 task.dummy.out.1
    (r'TASK.dummy.in(.+)', r'TASK.dummy.out(.+)'),
    ]


def sort_filenames(l):
    """ Sort the given list in the way that humans expect.
        http://www.codinghorror.com/blog/2007/12/sorting-for-humans-natural-sort-order.html
    """
    import re
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda file_pair: [ convert(c) for c in re.split('([0-9]+)', file_pair[0]) ]
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
        if self.is_example_run:
            patterns = EXAMPLE_PATTERNS
        else:
            patterns = EXAMPLE_PATTERNS + FULL_PATTERNS
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

        best_match = None
        for dirpath, _, filenames in os.walk(self.search_dir):
            for task in tasks_to_try:
                for pattern in patterns:
                    match = self.one_match(dirpath, filenames, task, pattern)
                    logging.debug('%s', match.__dict__)
                    if best_match is None or len(match.tests) > len(best_match.tests):
                        best_match = match
        if not best_match or not best_match.tests:
            logging.error('No test data found!')
            sys.exit(1)
        logging.info('Found %d test cases in %s', len(best_match.tests), best_match.dirpath)
        logging.info("Task name is '%s'", best_match.task)
        sort_filenames(best_match.tests)
        return best_match

    def one_match(self, dirpath, filenames, task, pattern):
        result = TestDataSearchMatch()
        result.dirpath = dirpath
        result.task = task
        result.tests = []
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
                result.tests.append((infile, outputs[seq]))
        return result

class TestDataSearchMatch:
    pass
