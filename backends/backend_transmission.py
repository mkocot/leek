import transmissionrpc
from backends import Backend, Torrent


class BackendTransmission(Backend):
    def __init__(self, conf):
        self.client = transmissionrpc.Client(
            address=conf['server']['address'],
            port=int(conf['server']['port']))

    def add_torrent(self, address, paused=True):
        torrent = self.client.add_torrent(address, paused=paused)
        return Torrent(torrent.hashString)