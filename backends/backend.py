class Torrent(object):
    _hash = 'NONE'
    def __init__(self, hash):
        self._hash = hash

    @property
    def hash(self):
        return self._hash
        
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