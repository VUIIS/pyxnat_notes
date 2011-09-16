#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xnat_util as xutil

#  Initialize XNAT
xnat = xutil.load_xnat()

#  Subjects belong to a project, so grab the project you'd like to put them in
pjt = xnat.select.project('BTest')

#  Batch Subject Creation
subs = ['sub%d' % i for i in range(1000, 1005)]
"""
gender: male | female
handedness: right | left
yob: four digit string
ethnicity: any string
"""

gender = ['male', 'female', 'male', 'female', 'female']
handedness = ['right', 'right', 'left', 'right', 'right']
yob = ['2000', '2001', '2004', '2002', '2001']
ethnicity = ['white', 'black', 'asian', 'hispanic', 'foo']

new_subs = []
for id, g, h, y, e in zip(subs, gender, handedness, yob, ethnicity):
    data = {'gender': g, 'handedness': h, 'yob': y, 'ethnicity': e} 
    new_sub = xutil.subject(pjt, id, data)
    new_subs.append(new_sub)

