#!/usr/bin/env python
# -*- coding: utf-8 -*-
__license__ = 'BSD 3-Clause'

import os
import subprocess as sp
import time
from glob import glob

from xnat.mail import mail
#  Simple way to connect to XNAT
from xnat.util import xnat

def dump():
    """ Dump database to rolling weekly directory

    Dumps can be found in /data/dumps/

    """
    dump_file = os.path.join('/', 'data', 'dumps', '%s.pg_dump' % time.strftime('%A').lower())
    cmd = 'pg_dump -f %s' % dump_file
    ec = sp.Popen(cmd.split()).wait()
    return dump_file, ec

def dh():
    out, ec = run_cmd('df -h')
    return out, ec

def run_cmd(cmd):
    """ Run shell command

    out: stdout/stderr (combined)
    ec: exit code
    """
    try:
        out = sp.check_output(cmd.split(), stderr=sp.STDOUT)
        ec = 0
    except sp.CalledProcessError as e:
        out = e.output
        ec = 1
    return out, ec

def tail(fp, n=10):
    out, ec = run_cmd('tail -n %d %s' % (n, fp))
    return out, ec

if __name__ == '__main__':
    """ Check health of XNAT system """
    body = ''

    body += "Running XNAT health checks...\n"
    body += "Began at %s\n\n" % time.strftime('%H:%M:%S')

    """ DB Dump """
    body += "Dumping database....\n"
    df, error = dump()
    if not error:
        body += "Successful database dump to %s\n\n" % df
    else:
        body += "Error dumping to %s\n\n" % df
    """ End DB dump """

    """ Disk usage """
    body += "Disk usage...\n"
    out, error = dh()
    body += out
    body += "End disk usage \n\n"

    """ DCM Relay Error files """
    body += "Begin Error files...\n"
    for err in glob(os.path.expanduser('~/dcmrelay/*.err')):
        text_lines = []
        text_lines.append("Begin %s..." % err)
        out, _ = tail(err, n=20)
        text_lines.append(out)
        text_lines.append("End %s.\n\n" % err)
        body += '\n'.join(text_lines)
    body += "End Error files.\n"

    """ Xnat statistics """
    body += "XNAT system statistics...\n"
    x = xnat()
    body += "# users: %d\n" % len(x.manage.users())
    all_projs = x.select.projects().get()
    body += "# projects: %d\n" % len(all_projs)
    #  There's probably a better way to do this, but for now...
    all_sessions = []
    for p in all_projs:
        proj = x.select.project(p)
        all_sessions.extend(proj.experiments().get())
    body += "# sessions: %d\n" % len(all_sessions)
    #  We could go deeper into database if we wanted...

    body += "Finish at %s" % time.strftime('%H:%M:%S')
    to = ['bennett.landman@vanderbilt.edu', 'scott.s.burns@vanderbilt.edu']
    sub = "XNAT Health Check %s" % time.strftime('%a %d %b %Y %H:%M')
    mail(to=to, subject=sub, body=body)
