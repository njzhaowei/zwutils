import os
import json
import logging
import logging.config

def logger(name=__name__, cfg=None):
    '''Get logger with name'''
    cfg = cfg  or 'conf/log.json'
    if os.path.exists(cfg):
        with open(cfg, 'r') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)
    return logger
