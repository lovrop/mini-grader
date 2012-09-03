import ctypes
import multiprocessing
import os
import re
import sys
import time

from subprocess import Popen, PIPE
from signal import SIGTERM

def cpu_count():
    return multiprocessing.cpu_count()


class PERFORMANCE_INFORMATION(ctypes.Structure):
    _fields = [("cb", ctypes.c_int32),
               ("CommitTotal", ctypes.c_size_t),
               ("CommitLimit", ctypes.c_size_t),
               ("CommitPeak", ctypes.c_size_t),
               ("PhysicalTotal", ctypes.c_size_t),
               ("PhysicalAvailable", ctypes.c_size_t),
               ("SystemCache", ctypes.c_size_t),
               ("KernelTotal", ctypes.c_size_t),
               ("KernelPaged", ctypes.c_size_t),
               ("KernelNonpaged", ctypes.c_size_t),
               ("PageSize", ctypes.c_size_t),
               ("HandleCount", ctypes.c_int32),
               ("ProcessCount", ctypes.c_int32),
               ("Threadcount", ctypes.c_int32)]
               
class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_int32),
                ("PageFaultCount", ctypes.c_int32),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]
  
  
class lPopen (Popen):
    '''Runs an executable, enforcing resource limits through periodic polling.'''

    def _kill (self):
        try: os.kill(self.pid, SIGTERM)
        except: pass

    def _refresh_time(self):
        creationtime = ctypes.c_ulonglong()
        exittime = ctypes.c_ulonglong()
        kerneltime = ctypes.c_ulonglong()
        usertime = ctypes.c_ulonglong()
        rc = ctypes.windll.kernel32.GetProcessTimes(
            self.hProcess,
            ctypes.byref(creationtime),
            ctypes.byref(exittime),
            ctypes.byref(kerneltime),
            ctypes.byref(usertime))    

        if rc:
            self.time = (kerneltime.value + usertime.value) / 10000000
            
            
    def _refresh_memory(self):
        pmc = PROCESS_MEMORY_COUNTERS()
        rc = ctypes.windll.psapi.GetProcessMemoryInfo(self.hProcess, ctypes.byref(pmc), ctypes.sizeof(pmc))
        if rc:
            self.vmpeak = pmc.PeakWorkingSetSize
   
        
    def _refresh_usage (self):
        self._refresh_time()
        self._refresh_memory()
            
    #
    # Generic methods
    # 
    
    def __init__ (self, *args, **keywords):
        self.time = 0
        self.vmpeak = 0
        self.timeout = False
        self.memout = False
        self.path = args[0]
        Popen.__init__(self, *args, **keywords)
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        self.hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, self.pid)
        
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
