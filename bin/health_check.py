#!/usr/bin/env python
# -*- coding: utf-8 -*-
__license__ = 'BSD 3-Clause'

import os
from subprocess import Popen
import time

from xnat.mail import mail


def run_cmdline(cmdline):
    """ Start a process"""
    return Popen(cmdline.split()).wait()

def dump():
    """ Dump database to rolling weekly directory
    
    Dumps can be found in /data/dumps/
    
    """
    dump_file = os.path.join('/', 'data', 'dumps', '%s.pg_dump' % time.strftime('%A').lower())    
    ec = run_cmdline(['pg_dump', '-f', dump_file])
    return dump_file, ec

if __name__ == '__main__':
    """ Check health of XNAT system """
    body = ''
    
    body += "Running XNAT health checks...\n"
    
    """ DB Dump code """
    
    body += "Dumping database....\n"    
    df, error = dump()
    if not error:
        body += "Successful database dump to %s" % df
    else:
        body += "Error dumping to %s" % df
    
    """ End DB dump """
    
    #  Continue adding health checks here, appending to body
    
    
    to = ['bennett.landman@vanderbilt.edu', 'scott.s.burns@vanderbilt.edu']
    sub = "XNAT Health Check %s" % time.strftime('%a %d %b %Y %H:%M:%s')
    
    mail(to=, subject=sub, body=body)