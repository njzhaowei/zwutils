import pytest
import shutil
from pathlib import Path

from zwutils.mthreading import multithread_task
from zwutils.network import multithread_request
from zwutils import fileutils

class TestMP:
    def test_mtask(self):
        num = 100
        shutil.rmtree('data', ignore_errors=True)
        args = [{'path':'data/p%s.txt'%i, 'txt':i} for i in range(num)]
        multithread_task(fileutils.writefile, args)
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