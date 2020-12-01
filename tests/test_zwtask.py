# -*- coding: utf-8 -*-
import os
import sys
import time

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.join(TEST_DIR, '..')
sys.path.insert(0, PARENT_DIR)

from zwutils.zwtask import ZWTask

def test(task, a, b):
    while True:
        time.sleep(3)
        print(a+b)

if __name__ == '__main__':
    # task = ZWTask(target=test, name='yewtest', args=(1, 2), c2server='http://localhost:8080/api/spider/status')
    # task.start()
    # task.join()

    # args = [(i, i+1) for i in range(3)]
    # ZWTask.run_processes(target=test, args_list=args, c2server='http://localhost:8080/api/spider/status')

    args = [(i, i+1) for i in range(3)]
    ZWTask.run_pooled(target=test, args_list=args, max_size=1, c2server='http://localhost:8080/api/spider/status')