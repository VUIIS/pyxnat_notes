#!/usr/bin/env python
# -*- coding: utf-8 -*-
__license__ = 'BSD 3-Clause'

import os
from ConfigParser import ConfigParser

cfg = ConfigParser()
cfg.read(os.path.join(os.path.expanduser('~'), '.vuiisxnat.cfg'))

def tl2dict(tl):
    """ Takes a list of 2-tuples and returns a dict """
    data = {}
    for k,v in tl:
        data[k] = v
    return data
    
rc = tl2dict(cfg.items('rc'))
email = tl2dict(cfg.items('email'))