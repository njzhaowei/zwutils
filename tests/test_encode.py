# -*- coding: utf-8 -*-
import pytest
from pathlib import Path
import zwutils.encode as enc

GBK_FILEPATH = './tests/data/encode_gb2312.txt'
UTF_FILEPATH = './tests/data/encode_utf8.txt'

def test_detect_file_encode():
    r = enc.detect_file_encode(GBK_FILEPATH)
    assert r['encoding'] == 'gb2312'
    r = enc.detect_file_encode(UTF_FILEPATH)
    assert r['encoding'] == 'utf-8'

def test_detect_data_encode():
    with open(GBK_FILEPATH, 'rb') as fp:
        s = fp.read()
    r = enc.detect_data_encode(s)
    assert r['encoding'] == 'gb2312'
    with open(UTF_FILEPATH, 'rb') as fp:
        s = fp.read()
    r = enc.detect_data_encode(s)
    assert r['encoding'] == 'utf-8'
