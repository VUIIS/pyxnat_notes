#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from ConfigParser import ConfigParser

"""
Before running this, save a file called .pycap.cfg (initial period so it's hidden)
in C:\Users\[yourname]\ (or $HOME/ on unix boxes). This file should look like:
[keys]
VUIIS-ProjectApp: [the api key from the emails]

Only once you've done this will the following code work
"""

cfg = ConfigParser()
cfg.read(os.path.join(os.path.expanduser('~'), '.pycap.cfg'))
api_key = cfg.get('keys', 'VUIIS-ProjectApp')

""" We did the above so as to hide our API key and not publish it to the world
when we push this code to github :) """