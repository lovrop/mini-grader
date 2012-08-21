import tempfile

import runlib

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
    
    def __init__(self, executable, inpath, refoutpath, checker):
        self.executable = executable
        self.inpath = inpath
        self.refoutpath = refoutpath
        self.checker = checker
        
        self.lpopen = None
        self.status = Runner.WAITING

    def run(self, time_limit, memory_limit):
        with open(self.inpath, 'rb') as infile:
            with tempfile.TemporaryFile() as outfile:
                self.status = Runner.RUNNING
                self.lpopen = runlib.lPopen(self.executable, stdin=infile, stdout=outfile)
                self.lpopen.lwait(tlimit=time_limit*100, mlimit=memory_limit*1024)
                self.status = Runner.CHECKING
                infile.seek(0)
                outfile.seek(0)
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
