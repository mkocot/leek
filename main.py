#!/usr/bin/env python3
import feeder
import config
import backends
import time
import logging
import sys
import signal
import argparse
import xdgpathlib
from updater import Updater

xdgpathlib.setAppName('leek')

logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(stream=sys.stderr))
logger.setLevel(logging.DEBUG)

configPath = xdgpathlib.appConfigDir('config.toml')

conf = config.config(configPath)

logger.setLevel(conf['global'].get('log_level', 'info').upper())
logoutput = conf['global'].get('log', 'stderr').lower()

if logoutput == 'stderr':
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler(stream=sys.stderr))

updater = Updater(conf)

def run_loop():
    while True:
        logger.debug('Checking updates')
        updater.fetch_and_add()
        logger.debug('Checking done')
        time.sleep(conf['global'].get('refresh', 600))

run_loop()