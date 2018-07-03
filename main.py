#!/usr/bin/env python3
import feeder
import config
import backends
import time
import logging
import sys
import signal
import argparse
from updater import Updater

logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(stream=sys.stderr))
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.toml')
args = parser.parse_args()

conf = config.config(args.config)

logger.setLevel(conf['global']['log_level'].upper())
logoutput = conf['global']['log']

if logoutput == 'stderr':
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler(stream=sys.stderr))

updater = Updater(conf)

def run_loop():
    while True:
        logger.debug('Checking updates')
        updater.fetch_and_add()
        logger.debug('Checking done')
        time.sleep(conf['global']['refresh'])

run_loop()