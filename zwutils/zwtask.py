import sched
from multiprocessing import  Process

from zwutils.config import Config
from zwutils.dlso import upsert_config, obj2dict

class ZWTask(Process):
    def __init__(self, target=None, args=None, cfg=None, **kwargs):
        super().__init__()
        cfgdef = {
            'c2server': 'localhost:13667',
        }
        self.cfg = upsert_config(None, cfgdef, cfg, kwargs)
        self.target = target
        self.args = args or ()
    
    def status_check(self):
        print('in check')

    def run(self):
        if self.target:
            self.target(self, *self.args)