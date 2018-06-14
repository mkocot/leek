from .backend import Torrent, TorrentInfo, Backend
from . import backend_transmission
from . import backend_dummy


__all__ = ['.backend', '.backend_transmission']

__BACKENDS = {
    'transmission': backend_transmission.BackendTransmission,
    'dummy': backend_dummy.BackendDummy
}

def create(name, conf):
    backend = __BACKENDS.get(name, None)
    if not backend:
        raise ValueError()
    return backend(conf)