import toml
import shelve
import collections

class DynamicConfig(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, name):
        self.store = shelve.open(name)

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return str(key)


class StaticConfig(dict):
    def __init__(self, file):
        self.file = file
        self.update(toml.load(self.file))

    def __setitem__(self, a, b):
        raise Exception("Set value not supported")
        
class Config(object):
    def __init__(self, file, seen):
        self.file = StaticConfig(file)
        # yes, its leak but who cares
        self.seen = dict() #  DynamicConfig(seen)
    
    def __getitem__(self, key):
        return self.file[key]

def config(file):
    return Config(file, 'seen.db')