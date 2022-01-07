# -*- coding: utf-8 -*-
import pytest

from zwutils.config import Config

def test_config():
    cfg = Config('data/test_config.json', default={'fld0':123})
    assert cfg.fld0==123

def test_set():
    cfg = Config()
    cfg.set('fld0', 123)
    assert cfg.fld0==123

def test_has():
    cfg = Config('data/test_config.json')
    assert 'fld0' in cfg
    cfg.set('fld1', 123)
    assert 'fld1' in cfg
    assert 'fld2' not in cfg