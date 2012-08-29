import logging
import sys

if sys.platform.startswith('win'):
    logging.error("Windows is (are?) not currently supported.  https://github.com/lovrop/mini-grader/issues/1")
    sys.exit(1)
else:
    if not sys.platform.startswith('linux'):
        logging.info("Platform '%s' is not explicitly supported.  Acting as if it is Linux but " +
                     "things may not work.")
    from .linux import cpu_count
