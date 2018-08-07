import config
import feeder
import logging
import shelve
from datetime import timedelta, datetime as dt
from re import finditer
from backends import TorrentInfo, create
from itertools import chain

_TIME_S2L = {'d':'days', 'h':'hours', 'm':'minutes', 's':'seconds', 'w':'weeks'}

class CacheItem(object):
    info = None
    isOk = False
    date = 0

    def __init__(self, info, date, isOk):
        self.info = info
        self.date = date
        self.isOk = isOk 

    @property
    def title(self):
        return self.info.title

    def __str__(self):
        return '{}, ok={}, date={}'.format(self.info, self.isOk, self.date)

class Cache(object):
    # fields
    # _logger - lo
    # _seen - cache
    def __init__(self, conf):
        self._logger = logging.getLogger(__class__.__name__)
        self._seen = shelve.open(conf['global'].get('seen', 'seen.cache'))
        # w d h m s
        staleRecordsString = conf['global'].get('stale-after', '1w')

        self._staleRecordsDelta = timedelta(**{_TIME_S2L[match.group(2).lower()]:int(match.group(1)) for match in finditer(r'(\d+)([wdhms]{1})', staleRecordsString)})

    # used for testing
    def _now(self):
        return dt.now()

    def isOk(self, torrent):
        try:
            return self._seen[torrent.hash].isOk
        except KeyError:
            return False

    def store(self, torrent, isOk=False):
        try:
            record = self._seen[torrent.hash]
            # only change 'bad' torrents
            # don't change good into bad ones
            if not record.isOk:
                record.isOk = isOk
                record.date = self._now()
        except KeyError:
            record = CacheItem(info=torrent, date=self._now(), isOk=isOk)

        self._seen[torrent.hash] = record
        self._store()


    def _store(self):
        self._seen.sync()

    def badItems(self):
        '''
        Returns only not already added torrents
        '''
        return (cache.info for h,cache in self._seen.items() if not cache.isOk)

    def removeStale(self):
        timecheck = self._now()
        for k,v in self._seen.items():
            if v.isOk and (timecheck - v.date) >= self._staleRecordsDelta:
                self._logger.info('Removing old entry from cache: {}'.format(v.title))
                self._seen.pop(k)
        self._store()

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

            if self.cache.isOk(torrent):
                self.logger.info('Already added')
                return

            if self.bckend.add_torrent(torrent):
                self.cache.store(torrent, True)
                return True
            # if we failed add info
            self.cache.store(torrent)
            self.logger.warn('Unable to add')
            return False
        except Exception:
            self.cache.store(torrent)
            self.logger.exception('Failed: %s', torrent)
            return False


    def fetch_and_add(self):
        for hit in chain(self.feed.parse(), self.cache.badItems()):
            self._add_torrent(hit)
        self.cache.removeStale()
