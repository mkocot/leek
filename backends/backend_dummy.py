from backends import Backend, Torrent

class BackendDummy(Backend):
    def __init__(self, conf):
        super().__init__(conf)

    def add_torrent(self, url, paused=True):
        return Torrent('None')