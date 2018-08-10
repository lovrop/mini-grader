import os
import re
import resource
import sys
import time

from subprocess import Popen, PIPE
from signal import SIGTERM

def cpu_count():
    '''Linux-specific implementation that tries to figure out the number of physical cores from /proc/cpuinfo.'''
    result = None
    try:
        with open('/proc/cpuinfo', 'r') as cpuinfo:
            coreid_re = re.compile(r'core id\s*:\s*([^\s]+)')
            coreids = set()
            for line in cpuinfo:
                match = coreid_re.match(line)
                if match:
                    coreids.add(match.group(1))
        result = len(coreids)
    except IOError:
        pass

    if not result:
        # Fall back to Python builtin
        import multiprocessing
        result = multiprocessing.cpu_count()
    return result


class lPopen (Popen):
    '''Runs an executable, enforcing resource limits through periodic polling.'''


    #
    # Linux specific methods
    #

    def _kill (self):
        try: os.kill(self.pid, SIGTERM)
        except: pass

    def _wrapped_read(self, path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except IOError as e:
            if e.errno == 2: # File not found
                return None
            raise

    def _refresh_usage (self):
        procstat = self._wrapped_read('/proc/%d/stat' % self.pid)
        if procstat is not None:
            stats = procstat.split(")")[1].split()
            self.time = max(self.time, int(stats[11]) + int(stats[12])) / 100

        procstatus = self._wrapped_read('/proc/%d/status' % self.pid)
        if procstatus is not None:
            tokens = procstatus.split()
            try:
                vmpeak = int(tokens[tokens.index("VmPeak:")+1]) * 1024
                if vmpeak <= 2**40:
                    self.vmpeak = vmpeak
                else:
                    # Probably dealing with an ASAN binary, do not report
                    # memory usage
                    self.vmpeak = 0

            except ValueError: # No entries
                pass

    #
    # Generic methods
    #

    def __init__ (self, *args, **keywords):
        self.time = 0
        self.vmpeak = 0
        self.timeout = False
        self.memout = False
        self.path = args[0]

        # Raise stack limit as high as it goes (hopefully unlimited)
        soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK, (hard, hard))

        # Now start the process
        Popen.__init__(self, *args, **keywords)

    def lwait (self, tlimit, mlimit):
        self._refresh_usage()
        while self.poll() is None and not (self.timeout or self.memout):
            self._refresh_usage()
            self.timeout = tlimit is not None and self.time > tlimit
            self.memout = mlimit is not None and self.vmpeak > mlimit
            time.sleep(0.01)
        self._refresh_usage()
        self._kill()
        self.exitcode = self.wait()
