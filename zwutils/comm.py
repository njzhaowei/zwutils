import sys
import time
from difflib import SequenceMatcher

def ismac():
    return True if sys.platform == 'darwin' else False

def iswin():
    return True if sys.platform == 'win32' else False

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

def list_intersection(a, b, ordered=False):
    if ordered:
        return [i for i, j in zip(a, b) if i == j]
    else:
        return list(set(a).intersection(b)) # choose smaller to a or b?
