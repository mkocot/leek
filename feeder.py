import feedparser
import collections
import re


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


TorrentInfo = collections.namedtuple('TorrentInfo',
                                     ['title', 'infoHash', 'magnetURI'])


class Feeder(object):
    feeds = []

    def add_feed(self, x):
        self.feeds.append(FeederItem(**x))

    def parse(self):
        result = []
        for f in self.feeds:
            urls = isinstance(f.url, list) and f.url or [f.url]
            for url in urls:
                parse = feedparser.parse(url)
                # if entries is empty, then loading data failed
                result.extend([
                    self.convert_entry(entry, f) for entry in parse.entries
                    if f.accept_entry(entry)
                ])
        return result

    def convert_entry(self, entry, f):
        # hacky wacky
        torrentHash = None
        magnet = entry.link
        if not f.link_from:
            if magnet and (not magnet.endswith('.torrent') and not magnet.startswith('magnet://')):
                magnet = None

            for k, v in entry.items():
                if torrentHash and magnet:
                    break
                if 'infohash' in k:
                    torrentHash = v
                if 'magnet' in k:
                    magnet = v
        else:
            magnet = entry[f.link_from]

        if not torrentHash:
            print('W', 'Empty hash, replace with magnet link')
            torrentHash = magnet

        return TorrentInfo(
            infoHash=torrentHash, magnetURI=magnet, title=entry.title)
