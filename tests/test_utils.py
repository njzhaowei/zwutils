# -*- coding: utf-8 -*-
import pytest
import time

import zwutils.comm as comm

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
