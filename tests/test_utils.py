# -*- coding: utf-8 -*-
import os
import pytest
import shutil

import zwutils.comm as comm
from zwutils.mthreading import multithread_task
from zwutils.network import multithread_request

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
        args = [{'path':'data/p%s'%i, 'dat':i} for i in range(num)]
        multithread_task(comm.writefile, args)
        count = len(os.listdir('data'))
        shutil.rmtree('data', ignore_errors=True)
        assert count == num

    def test_mrequest(self):
        num = 10
        urls = ['http://httpbin.org/get' for i in range(num)]
        settings = {
            'useragent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }
        rtn = multithread_request(urls, settings)
        assert len(rtn) == num