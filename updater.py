import config
import feeder
import logging
import shelve
from backends import TorrentInfo, create
from itertools import chain

class Cache(object):
    def __init__(self, conf):
        self.logger = logging.getLogger(__class__.__name__)
        self.seen = shelve.open(conf['global'].get('seen', 'seen.cache'))

    def add(self, torrent:TorrentInfo):
        self.seen[torrent.hash] = (torrent.title, torrent.link)
        self._store()

    def rem(self, torrent:TorrentInfo):
        if torrent.link in self.seen:
            del self.seen[torrent.hash]
            self._store()

    def _store(self):
        self.seen.sync()

    def items(self):
        return (TorrentInfo(t, l, h) for h,(t, l) in self.seen.items())

class Updater(object):
    def __init__(self, conf):
        self.cache = Cache(conf)
        self.conf = conf
        self.logger = logging.getLogger(__class__.__name__)
        self.feed = feeder.Feeder()
        self.bckend =  create(conf['global']['backend'], conf)
        for f in conf['feed']:
            if f.get('enabled', True):
                self.feed.add_feed(f)

    def _add_torrent(self, torrent):
        try:
            self.logger.info('Adding: %s', torrent.title)
            if self.bckend.add_torrent(torrent):
                self.cache.rem(torrent)
                return True
            self.logger.warn('Unable to add')
            return False
        except Exception:
            self.cache.add(torrent)
            self.logger.exception('Failed: %s', torrent)
            return False


    def fetch_and_add(self):
        for hit in chain(self.feed.parse(), self.cache.items()):
            self._add_torrent(hit)
