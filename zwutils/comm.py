import os
import sys
from pathlib import Path
import codecs
import json
from difflib import SequenceMatcher
import time

def ismac():
    return True if sys.platform == 'darwin' else False

def iswin():
    return True if sys.platform == 'win32' else False

def writefile(path, dat, isbin=False):
    flag = 'wb' if isbin else 'w'
    if not isbin and not isinstance(dat, str):
        dat = str(dat)
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(path, flag, 'utf-8') as fp:
        fp.write(dat)
        fp.flush()

def readfile(path):
    rtn = None
    with codecs.open(path, 'r', 'utf-8') as fp:
        rtn = fp.read()
    return rtn

def writejson(path, o):
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(path, 'w', 'utf-8') as fp:
        json.dump(o, fp)

def readjson(path):
    rtn = None
    if os.path.exists(path):
        with codecs.open(path, 'r', 'utf-8') as f:
            rtn = json.load(f)
    return rtn

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def dict2attr(kv):
    kv = kv or {}
    o = type('', (), {})()
    for key, val in kv.items():
        setattr(o, key, val)
    return o

def attr2dict(o):
    o = o or type('', (), {})()
    r = {}
    attrs = [a for a in dir(o) if not a.startswith('_')]
    for attr in attrs:
        r[attr] = getattr(o, attr)
    return r

def extend_attrs(o, kv):
    kv = kv or {}
    for key, val in kv.items():
        setattr(o, key, val)
    return o

def update_attrs(settings, kv):
    settings = settings or type('', (), {})()
    if isinstance(settings, dict):
        settings = dict2attr(settings)

    for key, val in kv.items():
        if hasattr(settings, key):
            setattr(settings, key, val)
    return settings

def print_duration(method):
    """Prints out the runtime duration of a method in seconds
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('%r %2.2f sec' % (method.__name__, te - ts))
        return result
    return timed
