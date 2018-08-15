from os import path, environ, makedirs
HOME = environ.get('HOME', path.expanduser('~'))

XDG_CONFIG_HOME = environ.get("XDG_CONFIG_HOME", path.join(HOME, ".config"))
XDG_CONFIG_DIRS = [XDG_CONFIG_HOME] + environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(":")
XDG_DATA_HOME = environ.get("XDG_DATA_HOME", path.join(HOME, ".local", "share"))
XDG_CACHE_HOME = environ.get("XDG_CACHE_HOME", path.join(HOME, ".cache"))
__APP_NAME = None

def setAppName(appName):
    global _APP_NAME
    _APP_NAME = appName

def getAppName():
    global _APP_NAME
    return _APP_NAME

def _appPath(base, create, file):
    confPath = path.join(base, getAppName())
    if create:
        makedirs(confPath, 0o700, exist_ok=True)
    return path.join(confPath, file)

def appConfigDir(file, create=False):
    return _appPath(XDG_CONFIG_HOME, create, file)

def appCacheDir(file, create=False):
    return _appPath(XDG_CACHE_HOME, create, file)