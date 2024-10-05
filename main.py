#!/usr/bin/env python3
# This is tha main core of multi launcher script

from concurrent.futures import thread
from time import sleep
import core.listeners as listeners
import logging
import logging.handlers
import os
import sys
import config.common_conf as settings


def init_logger() -> None:
    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_ON_FILE:
        handler = logging.handlers.BaseRotatingHandler(os.environ.get("LOGFILE", settings.LOGFILE))
    formatter = logging.Formatter(settings.LOGGING_FORMATTER)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", settings.LOG_LEVEL))
    root.addHandler(handler)


def main():
    global listener
    listener = listeners.init_listener()
    listener.run()

continue_process = True

while continue_process:
    try:
        init_logger()
        exit(main())
    except KeyboardInterrupt as e:
        logging.info("Exiting..")
        listener.close()
        continue_process = False
    except Exception:
        logging.exception("Exception in main()")
        if settings.ON_ERROR== 'retry':
            sleep(2000)
            logging.info("Trying to run service again..")
            continue
        else:
            exit(1)