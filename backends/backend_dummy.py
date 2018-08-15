from backends import Backend, Torrent

class BackendDummy(Backend):
    def __init__(self, conf):
        super().__init__(conf)

    def add_torrent(self, url, paused=True):
        print('DUMMY BACKEND: Adding torrent {}'.format(url))
        return Torrent('None')