import feedparser
import collections
import re
from urllib.request import urlopen
import logging
from backends import TorrentInfo

class FeederItem(object):
    url = ''
    link_from = ''
    pattern = {}

    @staticmethod
    def _convert(pattern):
        if isinstance(pattern, str):
            return {'title': pattern}
        if isinstance(pattern, dict):
            return pattern

    def __init__(self, url, pattern, link_from=None):
        self.url = url
        self.link_from = link_from and link_from.lower()
        if not isinstance(pattern, collections.Iterable):
            pattern = [pattern]
        self.pattern = [{
            k.lower(): re.compile(v)
            for k, v in self._convert(p).items()
        } for p in pattern]

    def accept_entry(self, entry):
        # 1) iterate over pattern groups
        # 2) all elements of groups mustch match
        # 3) any patter group match
        try:
            return any(
                all(p.search(entry.get(k, '')) for k, p in pg.items())
                for pg in self.pattern)
        except AttributeError as err:
            print('Invalid entry', err)
            return False


class Feeder(object):
    feeds = []
    logger = logging.getLogger('Feeder')

    def add_feed(self, x):
        self.feeds.append(FeederItem(**x))

    def parse(self):
        result = []
        for f in self.feeds:
            urls = isinstance(f.url, list) and f.url or [f.url]
            for url in urls:
                try:
                    self.logger.info('Loading info: %s', url)
                    content = self.download(url)
                    # it's probably hanging there for some obscure reason
                    # that's why we are passing raw text only
                    parse = feedparser.parse(content)
                    # if entries is empty, then loading data failed
                    result.extend([
                        self.convert_entry(entry, f) for entry in parse.entries
                        if f.accept_entry(entry)
                    ])
                except:
                    self.logger.exception('Failed url: %s', url)
        return result
    
    def download(self, url):
        """
        We ignore any errors that could be returned here.
        Any reported failure means this url need to be parsed again later
        """
        with urlopen(url, timeout=10) as httpsrc:
            return httpsrc.read()

    @staticmethod
    def __is_link_ok(link):
        return link.endswith('.torrent') \
               or link.startswith('magnet://')

    def convert_entry(self, entry, f):
        # hacky wacky
        link = [
            l.href for l in entry.links
            if l.type == 'application/x-bittorrent'
            or self.__is_link_ok(l.href)
        ]
        link = len(link) and link[0]
        hash = None
        if not f.link_from:
            for k, v in entry.items():
                if link and hash:
                    break
                if 'hash' in k:
                    hash = v
                if 'magnet' in k:
                    if not link and self.__is_link_ok(v):
                        link = v
        else:
            link = entry.get(f.link_from, None)

        return TorrentInfo(entry.title, link, hash)
