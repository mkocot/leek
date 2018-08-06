import transmissionrpc
from backends import Backend, Torrent
import urllib

class BackendTransmission(Backend):
    def __init__(self, conf):
        self.client = transmissionrpc.Client(
            address=conf['server']['address'],
            port=int(conf['server']['port']))

        # replace default name to something sane as we might get bounced
        # with default values. This is 'ugly' way but
        #  library soesn't allow to change it gently
        proper_opener = urllib.request.build_opener()
        proper_opener.addheaders = [('User-agent', 'leek/0.0 [python]')]
        urllib.request.install_opener(proper_opener)

    def add_torrent(self, torrent, paused=True):
        torrent = self.client.add_torrent(torrent.link, paused=paused)
        return Torrent(torrent.hashString)
