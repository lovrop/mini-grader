import os
import shutil
import subprocess
import tempfile

from . import platform_dependent

class Runner:
    '''Runs the executable on a single test case and grades the output.'''

    class Result:
        PASSED = 1
        WRONG_ANSWER = 2
        TIME_LIMIT = 3
        MEMORY_LIMIT = 4
        RUNTIME_ERROR = 5

    WAITING = 1
    RUNNING = 2
    CHECKING = 3
    DONE = 4

    def __init__(self, task_name, executable, inpath, refoutpath, checker, usaco_style_io):
        self.task_name = task_name
        self.executable = executable
        self.inpath = inpath
        self.refoutpath = refoutpath
        self.checker = checker
        self.usaco_style_io = usaco_style_io

        self.lpopen = None
        self.status = Runner.WAITING

    def run(self, time_limit, memory_limit):
        if not self.usaco_style_io:
            self._run_with_normal_io(time_limit, memory_limit)
        else:
            self._run_with_usaco_io(time_limit, memory_limit)

    def _run_with_normal_io(self, time_limit, memory_limit):
        # Normally, I/O goes through standard streams.  Open the input file
        # for stdin and a temporary file for stdout.
        with open(self.inpath, 'rb') as infile:
            with tempfile.TemporaryFile() as outfile:
                self.lpopen = platform_dependent.lPopen(self.executable, stdin=infile, stdout=outfile, stderr=subprocess.DEVNULL)
                self.status = Runner.RUNNING
                self.lpopen.lwait(tlimit=time_limit, mlimit=memory_limit)
                self.status = Runner.CHECKING
                infile.seek(0)
                outfile.seek(0)
                with open(self.refoutpath, 'rb') as refout:
                    self.grade(infile, outfile, refout)
                self.status = Runner.DONE

    def _run_with_usaco_io(self, time_limit, memory_limit):
        # In USACO-style tasks, the executable opens TASK.in and TASK.out
        # itself.
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(self.inpath, os.path.join(tmpdir, self.task_name + '.in'))
            outpath = os.path.join(tmpdir, self.task_name + '.out')
            self.lpopen = platform_dependent.lPopen(os.path.realpath(self.executable), cwd=tmpdir, stderr=subprocess.DEVNULL)
            self.status = Runner.RUNNING
            self.lpopen.lwait(tlimit=time_limit, mlimit=memory_limit)
            self.status = Runner.CHECKING
            with open(self.inpath, 'rb') as infile:
                with open(outpath, 'rb') as outfile:
                    with open(self.refoutpath, 'rb') as refout:
                        self.grade(infile, outfile, refout)
            self.status = Runner.DONE

    def grade(self, infile, outfile, refout):
        if self.lpopen.timeout:
            self.result = Runner.Result.TIME_LIMIT
        elif self.lpopen.memout:
            self.result = Runner.Result.MEMORY_LIMIT
        elif self.lpopen.exitcode != 0:
            self.result = Runner.Result.RUNTIME_ERROR
        else:
            self.result = self.check_output(infile, outfile, refout)

    def check_output(self, infile, outfile, refout):
        if self.checker.correct(infile, outfile, refout):
            return Runner.Result.PASSED
        else:
            return Runner.Result.WRONG_ANSWER

    def get_time(self):
        return self.lpopen.time if self.lpopen is not None else 0

    def get_memory(self):
        return self.lpopen.vmpeak if self.lpopen is not None else 0
