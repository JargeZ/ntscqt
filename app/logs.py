import sys

from loguru import logger

logger.add("ntscqt_last_debug_log.log", enqueue=True, mode='w')

