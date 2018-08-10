import os
import psutil
import resource
import signal
import sys
import threading
import time

from subprocess import Popen, PIPE

def cpu_count():
    return psutil.cpu_count(logical=False)

class lPopen(Popen):
    '''Runs an executable, enforcing resource limits through periodic polling.'''

    def __init__(self, *args, **keywords):
        self.time = 0
        self.vmpeak = 0
        self.timeout = False
        self.memout = False
        self._aborted = False
        self._abort_lock = threading.Lock()
        self._abort_cv = threading.Condition(self._abort_lock)
        self.on_osx = sys.platform.startswith('darwin')

        self._set_stack_limit()

        # Now start the process
        Popen.__init__(self, *args, **keywords)

        self.psutil_process = psutil.Process(self.pid)

    def lwait(self, tlimit, mlimit):
        self._refresh_usage()
        while self.poll() is None and not (self.timeout or self.memout):
            self._refresh_usage()
            self.timeout = tlimit is not None and self.time > tlimit
            self.memout = mlimit is not None and self.vmpeak > mlimit
            with self._abort_lock:
                if self._aborted:
                    break
                self._abort_cv.wait(0.01)
        self._refresh_usage()
        self._kill()
        self.exitcode = self.wait()

    def abort(self):
        with self._abort_lock:
            self._aborted = True
            self._abort_cv.notify()

    def _refresh_usage(self):
        try:
            with self.psutil_process.oneshot():
                times = self.psutil_process.cpu_times()
                self.time = max(self.time, times.user + times.system)

                mems = self.psutil_process.memory_info()
                # With psutil 5.1.3 / OSX 10.13 mems.vms is garbage, use `rss'
                # instead on OSX
                current_mem = mems.rss if self.on_osx else mems.vms
                if current_mem <= 2**40:
                    self.vmpeak = max(self.vmpeak, current_mem)
                else:
                    # Probably dealing with an ASAN binary, do not report
                    # memory usage
                    self.vmpeak = 0
        except psutil.NoSuchProcess:
            pass

    def _kill(self):
        try: os.kill(self.pid, signal.SIGKILL)
        except: pass

    def _set_stack_limit(self):
        # TODO: investigate this on OSX
        if not self.on_osx:
            # Raise stack limit as high as it goes (hopefully unlimited)
            soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
            resource.setrlimit(resource.RLIMIT_STACK, (hard, hard))
