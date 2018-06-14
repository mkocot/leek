import hashlib
import logging

class Torrent(object):
    _hash = 'NONE'
    def __init__(self, hash):
        self._hash = hash

    @property
    def hash(self):
        return self._hash


class TorrentInfo(Torrent):
    title = ''
    link = ''

    def __init__(self, title, link, hash):
        logger = logging.getLogger(__class__.__name__)
        if not title:
            raise ValueError('title')
        if not link:
            raise ValueError('link')
        if not hash:
            hash = hashlib.sha256(link.encode('utf-8')).hexdigest()
            logger.debug('Generate: Hash({}) = {}'.format(link, hash))

        super().__init__(hash)

        self.title = title
        self.link = link

    def __str__(self):
        return 'Torrent(link={}, hash={}, title={})'.format(
            self.link, self.hash, self.title)

    def __repr__(self):
        return self.__str__()
        
class Backend(object):
    def __init__(self, conf):
        self.conf = conf
        pass

    def add_torrent(self, url, paused=True):
        raise NotImplementedError()

    def reload(self):
        pass

    def connect(self):
        pass