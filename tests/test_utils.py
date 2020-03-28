# -*- coding: utf-8 -*-
import os
import time
import pytest
import shutil
import struct
from pathlib import Path

import zwutils.comm as comm
from zwutils.mthreading import multithread_task
from zwutils.network import multithread_request

def multirun_cbfunc(s):
    return 'result: %s'%s

class TestUtils:
    # pylint: disable=no-member
    def test_dict2attr(self):
        r = comm.dict2attr({
            'ks': 'v1',
            'kn': 2,
            'ka': [1, '2'],
            'kd': {'1':1, '2':2},
            'knone': None
        })
        r2 = comm.dict2attr(None)
        assert r.ks == 'v1'
    
    def test_attr2dict(self):
        o = type('', (), {})()
        o.a1 = 'a'
        o.a2 = 'b'
        r = comm.attr2dict(o)
        assert r['a1'] == 'a'

    def test_extend_attr(self):
        o = comm.dict2attr({'a':'a', 'b':'b'})
        comm.extend_attrs(o, {'a':'aa', 'c':1})
        assert o.a == 'aa' and o.c == 1

    def test_update_attrs(self):
        o = comm.dict2attr({'a':'a', 'b':'b'})
        comm.update_attrs(o, {'a':'aa', 'c':1})
        assert o.a == 'aa' and not hasattr(o, 'c')

        o = comm.update_attrs({'a':'a', 'b':'b'}, {'a':'aa', 'c':1})
        assert o.a == 'aa' and not hasattr(o, 'c')

        o = comm.update_attrs(None, {'a':'aa', 'c':1})
        assert not comm.attr2dict(o) # {}
    
    def test_mtask(self):
        num = 100
        shutil.rmtree('data', ignore_errors=True)
        args = [{'path':'data/p%s.txt'%i, 'txt':i} for i in range(num)]
        multithread_task(comm.writefile, args)
        count = len( list(Path('data').glob('*.txt')) )
        shutil.rmtree('data', ignore_errors=True)
        assert count == num

    def test_mrequest(self):
        num = 3
        urls = ['http://httpbin.org/get' for i in range(num)]
        settings = {
            'useragent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }
        rtn = multithread_request(urls, settings)
        assert len(rtn) == num
    
    def test_multicmd(self):
        args = ['.', '/']
        cmds = [['ls', '-l', a] for a in args]
        r = comm.multiprocess_cmd(cmds)
        assert len(r) == len(args)
    
    def test_multirun(self):
        num = 10
        args = [(a,) for a in range(num)]
        r = comm.multiprocess_run(multirun_cbfunc, args)
        assert len(r) == num
    
    def test_binfile(self):
        p = 'data/binfile'
        arr = [10, 20, 30, 40, 92]
        dat = struct.pack('5B', *arr)
        comm.writebin(p, dat)
        s = os.path.getsize(p)
        d = comm.readbin(p)
        a = struct.unpack('5B', d)
        shutil.rmtree('data', ignore_errors=True)
        assert s == len(arr) and len(comm.list_intersection(arr, a)) == 5