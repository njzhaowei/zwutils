import time
import threading
import socket
from multiprocessing import Process
import psutil
import requests

from zwutils.dlso import upsert_config

class ZWTask(Process):
    STOP = 'stop'
    RUN = 'run'

    def __init__(self, target=None, name=None, args=None, daemon=None, cfg=None, **kwargs):
        super().__init__(name=name)
        cfgdef = {
            'c2server': 'http://localhost:13667/api/spider/status',
            'report_sleep': 3,
            'report_request_timeout': 3,
        }
        self.cfg = upsert_config(None, cfgdef, cfg, kwargs)
        self.hostname = socket.gethostname()
        self.target = target
        self.daemon = daemon

        _args = args or ()
        self.args = [self]
        self.args.extend(list(_args))

    def status_check(self):
        cfg = self.cfg
        while True:
            try:
                payload = {
                    'hname': self.hostname,
                    'pid': self.pid,
                    'pname': self.name,
                }
                if self.daemon:
                    o = self.daemon(self)
                    for p in o:
                        payload[p] = o[p]
                try:
                    r = requests.post(url=cfg.c2server, json=payload, timeout=cfg.report_request_timeout)
                    if r.status_code == 200:
                        r = r.json()
                        print('%s code: %s'%(self.name, r['code']))
                        if r['code'] == 1:
                            return
                except requests.exceptions.Timeout:
                    pass
                except requests.exceptions.ConnectionError:
                    pass
                time.sleep(cfg.report_sleep)
            except Exception as ex:
                pass

    def run(self):
        if self.target:
            thread_worker = threading.Thread(target=self.target, args=self.args, daemon=True)
            thread_checker = threading.Thread(target=self.status_check, daemon=True)
            thread_worker.start()
            thread_checker.start()
            thread_checker.join()
        print('%s return.'%self.name)
        exit(0)

    def suspend(self):
        print('%s suspend.'%self.name)
        if self.is_finish():
            return
        _psobj = psutil.Process(self.pid)
        _psobj.suspend()
    
    def resume(self):
        print('%s resume.'%self.name)
        if self.is_finish():
            return
        _psobj = psutil.Process(self.pid)
        _psobj.resume()
    
    def status(self):
        _psobj = psutil.Process(self.pid)
        if self.is_finish():
            return psutil.STATUS_STOPPED
        return _psobj.status()
    
    def is_finish(self):
        return self.exitcode == 0
    
    @classmethod
    def run_processes(cls, target=None, name_prefix=None, args_list=None, cfg=None, **kwargs):
        name_prefix = name_prefix or 'zwtask'
        args_list = args_list or []
        procs = []
        if target:
            for i,args in enumerate(args_list):
                pname = '%s-%d' % (name_prefix, i)
                proc = ZWTask(target=target, name=pname, args=args, cfg=cfg, **kwargs)
                procs.append(proc)
                proc.start()
        for proc in procs:
            proc.join()
    
    @classmethod
    def run_pooled(cls, target=None, name_prefix=None, args_list=None, max_size=5, proc_time=5, cfg=None, **kwargs):
        name_prefix = name_prefix or 'zwtask'
        args_list = args_list or []
        if not target:
            return

        running = []
        waiting = []
        for i,args in enumerate(args_list):
            pname = '%s-%d' % (name_prefix, i)
            proc = ZWTask(target=target, name=pname, args=args, cfg=cfg, **kwargs)
            proc.start()
            proc.suspend()
            waiting.append(proc)

        while True:
            for i in range(len(running)-1, -1, -1):
                p = running[i]
                p.suspend()
                if p.is_finish():
                    p.terminate()
                else:
                    waiting.append(p)
                running.pop()

            arr = waiting[:max_size] if len(waiting)>max_size else waiting
            for p in arr:
                running.append(p)
                waiting.pop(0)
                p.resume()
            if len(running)==0 and len(waiting)==0:
                break
            time.sleep(proc_time)
