# -*- coding: utf-8 -*-
import pytest
import os
import struct
import shutil
from pathlib import Path

from zwutils import dlso
from zwutils import fileutils

def setup_module():
    shutil.rmtree('data/test/unzip', ignore_errors=True)
    fileutils.rmfile('data/test/binfile', ignore_miss=True)
    fileutils.rmfile('data/test/file1.zip', ignore_miss=True)
    fileutils.rmfile('data/test/文件4.zip', ignore_miss=True)
    fileutils.rmfile('data/test/dir1.zip', ignore_miss=True)

def teardown_module():
    setup_module()

def test_binfile():
    pth = 'data/test/binfile'
    arr = [10, 20, 30, 40, 92]
    dat = struct.pack('5B', *arr)
    fileutils.writebin(pth, dat)
    s = os.path.getsize(pth)
    d = fileutils.readbin(pth)
    a = struct.unpack('5B', d)
    assert s == len(arr) and len(dlso.list_intersection(arr, a)) == 5

def test_md5():
    md5 = fileutils.md5('docs/pytest.pdf')
    assert md5 == 'd2e81dddfd92aa86233be7c18bf3b5d8'

def test_zip():
    r = fileutils.zip('data/test/file1.txt', 'data/test/file1.zip', pwd='123')
    assert r and Path('data/test/file1.zip').stat().st_size > 0
    r = fileutils.zip('./data/test/文件4.txt', pwd='123')
    assert r and Path('data/test/文件4.zip').stat().st_size > 0
    r = fileutils.zip('./data/test/dir1', 'data/test/dir1.zip', pwd='123')
    assert r and Path('data/test/dir1.zip').stat().st_size > 0

def test_unzip():
    fileutils.unzip('data/test/dir1.zip', 'data/test/unzip', pwd='123')
    assert os.listdir('data/test/unzip')
