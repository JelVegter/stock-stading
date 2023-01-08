import logging
import logging.config

logging.config.fileConfig("logging.ini")
logger = logging.getLogger("logger_root")
logger.debug("DEBUG MESSAGE")
logger.info("INFO MESSAGE")
logger.critical("CRITICAL MESSAGE")
