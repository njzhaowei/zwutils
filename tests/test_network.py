# -*- coding: utf-8 -*-
import pytest
import shutil
import requests
from pathlib import Path

from zwutils import fileutils
import zwutils.network as network

BASEPATH = Path('./tests/data/network')
TEMPPATH = BASEPATH / 'tmp'

def setup_module():
    teardown_module()
    TEMPPATH.mkdir(parents=True, exist_ok=True)

def teardown_module():
    fileutils.rmdir(TEMPPATH)

def test_ping():
    ip = network.ping('baidu.com')
    assert ip and '.' in ip

def test_get_html():
    r = network.get_html('http://www.baidu.com')
    assert r.startswith('<!DOCTYPE html><!--STATUS OK-->')

def test_downfile():
    url = 'https://dss1.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/weather/icons/a2.png'
    r = network.downfile(url, settings={'method':'get'}, outpath=TEMPPATH, filename='weatherimage.png')
    assert Path(r).exists()

def test_check_connect():
    r = network.check_connect(['http://www.baidu.com', 'http://123.com'])
    assert r[0][1] == True and r[1][1] == False