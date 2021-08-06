import sys

from loguru import logger

logger.add(sys.stderr, level="DEBUG")
logger.add("vhs_last_debug_log.log", enqueue=True, mode='w')

