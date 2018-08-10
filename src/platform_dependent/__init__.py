import logging
import sys

try:
    # Use psutil if available
    import psutil
    from .psutil import cpu_count, lPopen
except ImportError:
    if sys.platform.startswith('win'):
        from .windows import cpu_count, lPopen
    else:
        if not sys.platform.startswith('linux'):
            logging.info("Platform '%s' is not explicitly supported.  Acting as if it is Linux but " +
                         "things may not work.")
        from .linux import cpu_count, lPopen
