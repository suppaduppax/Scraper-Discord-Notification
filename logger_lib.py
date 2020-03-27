#!/usr/bin/env python3
import sys
import os
import importlib

import logging
from logging.handlers import RotatingFileHandler

import settings_lib

current_directory = os.path.dirname(os.path.realpath(__file__))

log_path = current_directory + "/logs"
log_file_debug = "debug.log"
log_file_cron = "cron.log"

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = RotatingFileHandler(f"{log_path}/{log_file_debug}", maxBytes=32000, backupCount=5)
fileHandler.setFormatter(logFormatter)

CRON_HANDLER = RotatingFileHandler(f"{log_path}/{log_file_cron}", maxBytes=32000, backupCount=5)
CRON_HANDLER.setFormatter(logFormatter)

rootLogger.addHandler(fileHandler)

#consoleHandler = logging.StreamHandler()
#consoleHandler.setFormatter(logFormatter)
#rootLogger.addHandler(consoleHandler)

rootLogger.setLevel(logging.INFO)

INFO = logging.INFO
WARNING = logging.WARNING
DEBUG = logging.DEBUG
ERROR = logging.ERROR


def add_handler(handler):
    rootLogger.addHandler(handler)

def log(level, s, **kwargs):
    if not isinstance(levels, list):
       level = [level]

    log_func = {
        logging.debug : debug,
        logging.info : info,
        logging.warning : warning,
        logging.error : error
    }

    log_func[level](s, **kwargs)

def log_print(level, s, **kwargs):
    log(level, s, **kwargs)
    print(s)

def set_level(level):
    logging.level = level

def info(s, **kwargs):
    logging.info(s, **kwargs)

def info_print(s, **kwargs):
    info(s, **kwargs)
    print(s)

def warning(s, **kwargs):
    logging.warning(s, **kwargs)

def warning_print(s, **kwargs):
    warning(s, **kwargs)
    print(s)

def debug(s, **kwargs):
    logging.debug(s, **kwargs)

def debug_print(s, **kwargs):
    debug(s, **kwargs)
    print(s)

def error(s, **kwargs):
    logging.error(s, **kwargs)

def error_print(s, **kwargs):
    error(s, **kwargs)
    print(s)


