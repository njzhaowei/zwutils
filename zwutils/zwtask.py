import psutil
from multiprocessing import Process

from zwutils.dlso import upsert_config
from zwutils.logger import cologger

class ZWTask(Process):
    def __init__(self, target=None, name=None, args=None, daemon=True, cfg=None, **kwargs):
        super().__init__(name=name, daemon=daemon)
        cfgdef = {}
        self.cfg = upsert_config(None, cfgdef, cfg, kwargs)

        self.target = target
        self.name = name
        self.args = [self]
        self.args.extend(list(args or ()))

    def run(self):
        cfg = self.cfg
        log = self.logger()
        if self.target is None:
            exit(1)
        log.info('Process #%s start.', self.pid)
        self.target(*self.args)
        log.info('Process #%s return.', self.pid)
        exit(0)
    
    def status(self):
        _psobj = psutil.Process(self.pid)
        if self.is_finish():
            return psutil.STATUS_STOPPED
        elif not psutil.pid_exists(self.pid):
            return psutil.STATUS_STOPPED
        return _psobj.status()
    
    def is_finish(self):
        return self.exitcode == 0
    
    def logger(self):
        self.log = cologger(__name__, self.name or self.pid)
        return self.log
