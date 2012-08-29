import re

def cpu_count():
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
