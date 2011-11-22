#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Scott Burns <scott.s.burns@gmail.com>'

import sys
from xnat.util import xnat

try:
    pwd = raw_input('password:')
except EOFError:
    sys.exit(1)

cmd = '/home/xnat/xnat/pipeline_1_5_3_mail/image-tools/WebBasedQCImageCreator -session {sess} -project {p} -xnatId {id} -host http://masi.vuse.vanderbilt.edu/xnat -u admin -pwd {pwd} -raw'

x = xnat()
all_projs = x.select.projects().get('obj')
for xp in all_projs:
    subs, sobjs = xp.subjects().get('label', 'obj')
    for sub, sobj in zip(subs, sobjs):
        exps, eobjs = sobj.experiments().get('label', 'obj')
        for session, eobj in zip(exps, eobjs):
            print cmd.format(sess=session, p=xp.label(), id=eobj.id(), pwd=pwd)