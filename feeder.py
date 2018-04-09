import feedparser
import collections
import re

'''
        <torrent:contentLength
        <torrent:infoHash>
        <torrent:magnetURI>
        <torrent:seeds>
        <torrent:peers>
        <torrent:verified>
        <torrent:fileName>
'''

class FeederItem(object):
    url = ''
    pattern = None
    
    def __init__(self, url, pattern):
        self.url = url
        self.pattern = [re.compile(pattern) for pattern in pattern]

TorrentInfo = collections.namedtuple('TorrentInfo', ['title', 'infoHash', 'magnetURI'])

class Feeder(object):
    feeds = []
    def add_feed(self, x):
        self.feeds.append(FeederItem(**x))

    def parse(self):
        result = []
        for f in self.feeds:
            parse = feedparser.parse(f.url)
            if parse.status == 200:
                result.extend([self.convert_entry(entry) for entry in parse.entries if self.accept_entry(entry, f.pattern)])
            else:
                print('broken', f.url)
        return result

    def accept_entry(self, entry, patterns):
        try:
            return any(p.match(entry.title) for p in patterns)
        except AttributeError as err:
            print('Invalid entry', err)
            return False

    def convert_entry(self, entry):
        # hacky wacky
        torrentHash = None
        magnet = entry.link
        for k,v in entry.items():
            if torrentHash and magnet:
                break
            if 'infohash' in k:
                torrentHash = v
            if 'mangnet' in k:
                magnet = v
        
        if not torrentHash:
            print('W', 'Empty hash, replace with magnet link')
            torrentHash = magnet

        return TorrentInfo(infoHash=torrentHash,
                           magnetURI=magnet,
                           title=entry.title)
