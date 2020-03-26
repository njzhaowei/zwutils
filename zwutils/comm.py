import os
import sys
import time
import subprocess
import codecs
import json
import csv
import logging

from pathlib import Path
from difflib import SequenceMatcher
from concurrent.futures import ProcessPoolExecutor, as_completed

def ismac():
    return True if sys.platform == 'darwin' else False

def iswin():
    return True if sys.platform == 'win32' else False

def writefile(path, txt, enc='utf-8'):
    if not isinstance(txt, str):
        txt = str(txt)
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(path, 'w', enc) as fp:
        fp.write(txt)
        fp.flush()

def readfile(path, enc='utf-8'):
    rtn = None
    with codecs.open(path, 'r', enc) as fp:
        rtn = fp.read()
    return rtn

def writebin(path, dat):
    if not isinstance(dat, bytes):
        logging.error('[zwutils] dat is not bytes when write bin.')
        return
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as fp:
        fp.write(dat)
        fp.flush()

def readbin(path):
    r = None
    with open(path, 'rb') as fp:
        r = fp.read()
    return r

def writejson(path, o):
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(path, 'w', 'utf-8') as fp:
        json.dump(o, fp)

def readjson(path):
    rtn = None
    if os.path.exists(path):
        with codecs.open(path, 'r', 'utf-8') as fp:
            rtn = json.load(fp)
    return rtn

def writecsv(path, array2d, delimiter=','):
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(path, 'w', 'utf-8') as fp:
        writer = csv.writer(fp, delimiter=delimiter)
        writer.writerows(array2d)

def readcsv(path):
    rtn = None
    if os.path.exists(path):
        with codecs.open(path, 'r', 'utf-8') as fp:
            reader = csv.reader(fp)
            rtn = list(reader)
    return rtn

def file_encode_convert(src, dst, src_encode='utf-8', dst_encode='gbk'):
    src_encode = src_encode.lower()
    dst_encode = dst_encode.lower()
    with codecs.open(src, 'r', src_encode) as fp:
        new_content = fp.read()
    with codecs.open(src, 'w', dst_encode) as fp:
        fp.write(new_content)
        fp.flush()

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

def multiprocess_cmd(cmds, max_workers=3):
    rtn = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        cmds = list(cmds)
        futures = [executor.submit(subprocess.run, cmd) for cmd in cmds]
        for future in as_completed(futures):
            r = future.result()
            rtn.append(r)
    return rtn

def multiprocess_run(cbfunc, args, max_workers=3):
    rtn = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        args = list(args)
        futures = [executor.submit(cbfunc, arg) for arg in args]
        for future in as_completed(futures):
            r = future.result()
            rtn.append(r)
    return rtn

def list_intersection(a, b, ordered=False):
    if ordered:
        return [i for i, j in zip(a, b) if i == j]
    else:
        return list(set(a).intersection(b)) # choose smaller to a or b?
