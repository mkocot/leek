#!/usrb/bin/env python3
import feeder
import config
import backends
import time
import logging
import sys
import signal
import argparse

logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(stream=sys.stderr))
logger.setLevel(logging.DEBUG)


conf = config.config('config.toml')

logger.setLevel(conf['global']['log_level'].upper())
logoutput = conf['global']['log']

if logoutput == 'stderr':
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler(stream=sys.stderr))


feed = feeder.Feeder()
bckend =  backends.create(conf['global']['backend'], conf)

for f in conf['feed']:
    if f.get('enabled', True):
        feed.add_feed(f)

def fetch_and_add():
    for hit in feed.parse():
        try:
            logger.info('Adding: %s', hit.title)
            torrent = bckend.add_torrent(hit.link)
            if hit.link in conf.seen:
                del conf.seen[hit.hash]
        except Exception:
            logger.exception('Failed: %s', hit)
            conf.seen[hit.hash] = (hit.title, hit.link)

def run_loop():
    while True:
        logger.debug('Checking updates')
        fetch_and_add()
        logger.debug('Checking done')
        time.sleep(conf['global']['refresh'])

run_loop()