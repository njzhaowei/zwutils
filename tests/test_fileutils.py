# -*- coding: utf-8 -*-
import pytest
import os
import struct
import shutil
from pathlib import Path

from zwutils import dlso
from zwutils import fileutils

BASEPATH = Path('./tests/data/fileutils')
TEMPPATH = BASEPATH / 'tmp'

def setup_module():
    shutil.rmtree(TEMPPATH, ignore_errors=True)

def teardown_module():
    setup_module()

def test_binfile():
    pth = TEMPPATH / 'binfile'
    arr = [10, 20, 30, 40, 92]
    dat = struct.pack('5B', *arr)
    fileutils.writebin(pth, dat)
    s = os.path.getsize(pth)
    d = fileutils.readbin(pth)
    a = struct.unpack('5B', d)
    assert s == len(arr) and len(dlso.listinter(arr, a)) == 5

def test_md5():
    md5 = fileutils.md5('docs/libdocs/pytest.pdf')
    assert md5 == 'd2e81dddfd92aa86233be7c18bf3b5d8'

def test_zip():
    r = fileutils.zip(BASEPATH / 'file1.txt', TEMPPATH / 'file1.zip', pwd='123')
    assert r and Path(TEMPPATH / 'file1.zip').stat().st_size > 0
    r = fileutils.zip(BASEPATH / 'dir1', TEMPPATH / 'dir1.zip', pwd='123')
    assert r and Path(TEMPPATH / 'dir1.zip').stat().st_size > 0

def test_unzip():
    fileutils.unzip(TEMPPATH / 'dir1.zip', TEMPPATH / 'unzip', pwd='123')
    assert os.listdir(TEMPPATH / 'unzip')
