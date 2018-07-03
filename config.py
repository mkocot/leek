import toml
import shelve

class StaticConfig(dict):
    def __init__(self, file):
        self.file = file
        self.update(toml.load(self.file))

    def __setitem__(self, a, b):
        raise Exception("Set value not supported")
        
class Config(object):
    def __init__(self, file):
        self.file = StaticConfig(file)
    
    def __getitem__(self, key):
        return self.file[key]

def config(file):
    return Config(file)