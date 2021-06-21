# -*- coding: utf-8 -*-
import os
import sys
import time
from multiprocessing import Queue
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zwutils.zwtask import ZWTask
from zwutils.logger import logger
LOG = logger(__name__)

def test(task, a, b):
    try:
        for i in range(10):
            log = task.logger()
            q = task.queue
            n = task.name
            s = q.get(block=False)
            if not s.startswith(n):
                q.put(s)
            else:
                log.info('Task %d, %s, (a,b):(%d,%d), queue: %s', i, task.pid, a, b, s)
            time.sleep(3)
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    LOG.info('Main process start.')
    args = [(i,i+1) for i in range(3)]
    queue = Queue()
    for i in range(3):
        queue.put('Task-0-%d'%i)
    for i in range(2):
        queue.put('Task-1-%d'%i)
    queue.put('Task-2-%d'%i)

    tasks, q, a, v = ZWTask.run_tasks(test, args, queue=queue)

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