# -*- coding: utf-8 -*-
import pytest
from tests.conftest import rmfile, rmdir
from zwutils.httputils import *

URL_BING = 'https://cn.bing.com/'
URL_BADU = 'https://www.baidu.com/'
URL_TEST = 'http://httpbin.org/'

BASEPATH = Path('./tests/data/httputils')
TEMPPATH = BASEPATH / 'tmp'

def setup_module():
    teardown_module()
    TEMPPATH.mkdir(parents=True, exist_ok=True)

def teardown_module():
    rmdir(TEMPPATH)

def test_ping():
    ip = ping('baidu.com')
    assert ip and '.' in ip

def test_head():
    r = head(URL_TEST)
    assert r.request.method == 'HEAD' and r.status_code == 200

def test_request():
    r = request(URL_TEST)
    assert r.request.method == 'GET' and r.status_code == 200
    r = get(URL_TEST+'get')
    assert r.request.method == 'GET' and r.status_code == 200
    r = post(URL_TEST+'post')
    assert r.request.method == 'POST' and r.status_code == 200

def test_get_html():
    r = get_html(URL_TEST)
    assert r.startswith('<!DOCTYPE html>')

def test_multithread_request():
    r = multithread_request( [URL_BING, URL_BADU] )
    assert len(r)==2 and '必应' in r[0].resp.text and '百度' in r[1].resp.text

def test_download():
    url = 'https://dss1.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/weather/icons/a2.png'
    r = download(url, outpath=TEMPPATH, isdir=True)
    assert Path(r).exists()

def test_check_connect():
    r = check_connect([URL_TEST])
    assert r[0][1] == True

def test_cookies():
    cookiesspath = TEMPPATH / 'cookies.json'
    resp = get(URL_BADU)
    r = save_cookies(resp, cookiesspath)
    assert r and cookiesspath.exists()
    r = load_cookies(cookiesspath)
    assert r

def test_get_request_kwargs():
    o = DEFAULT_CONFIG
    r = get_request_kwargs(o)
    assert all([ r[p] == o['requests'][p] for p in o['requests'] ])