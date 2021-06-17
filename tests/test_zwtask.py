# -*- coding: utf-8 -*-
import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zwutils.zwtask import ZWTask
from zwutils.logger import logger
LOG = logger(__name__)

def test(task, a, b):
    try:
        for i in range(3):
            log = task.logger()
            log.info('Task %d, %s', i, task.pid)
            time.sleep(3)
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    tasks = [ZWTask(test, 'test%02d'%i, (i,i+1)) for i in range(3)]
    for t in tasks:
        t.start()
    
    while True:
        for i, o in enumerate(tasks):
            if o.is_finish():
                o.terminate()
                tasks[i] = None
            elif not o.is_alive():
                tasks[i] = None
        tasks = [o for o in tasks if o]
        if not tasks:
            break
    LOG.info('Main process exit.')