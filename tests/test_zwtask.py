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
    task = ZWTask(target=test, args=(1, 2))
    task.start()
    task.join()