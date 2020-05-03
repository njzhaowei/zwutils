import os
import json
import logging
import logging.config
from pathlib import Path

def logger(name=__name__, cfg=None):
    '''Get logger with name'''
    cfg = cfg  or 'conf/log.json'
    if os.path.exists(cfg):
        with open(cfg, 'r') as f:
            config = json.load(f)
            handlers = config['handlers']
            for h,o in handlers.items():
                if 'filename' in o and not Path(o['filename']).parent.exists():
                    Path(o['filename']).parent.mkdir(parents=True, exist_ok=True)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)
    return logger
