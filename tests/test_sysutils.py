# -*- coding: utf-8 -*-
import pytest
from pathlib import Path

from zwutils.sysutils import *

from zwutils import fileutils
BASEPTH = Path('./tests/data/sysutils')
TEMPPTH = BASEPTH / 'tmp'
def setup_module():
    teardown_module()
    TEMPPTH.mkdir(parents=True, exist_ok=True)

def teardown_module():
    fileutils.rmdir(TEMPPTH)

def test_proc():
    r = pids_by_name()
    assert len(r)>0

    r = pids_by_name('svchost.exe')
    assert len(r) > 0

    r = pids_by_name(r'svchost.*')
    assert len(r) > 0

def test_run_shell():
    r = run_shell('dir', 'C:\\')
    assert len(r) != 0

def test_sys_usage():
    r = get_sys_usage()
    assert len(r) == 2

def test_write_pidfile():
    dirpth = TEMPPTH / 'pids'
    r = write_pidfile(dir=dirpth)
    assert r.exists()