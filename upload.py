#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xnat_util as xutil

#  Initialize XNAT
xnat = xutil.xnat()

#  Subjects belong to a project, so grab the project you'd like to put them in
pjt = xutil.project(xnat, 'BTest')

#  Grab a subject
sub = xutil.subject(pjt, 'sub1000')

#  Grab the experiment
exp = xutil.experiment(sub, 'fmri_swr')

#  first run
run = xutil.scan(exp, 'run1')

#  Upload nifti
xutil.add_nifti(run, 'fmri', '/Volumes/Data/NFRO1/Pre/1005/M1/SWR1.nii')

"""  If you can figure out other metadata (from external resources?), 
you can also put that in """

run2 = xutil.scan(exp, 'run2')
md = {'quality': 'Good', 'scanner': 'Phillips', 'modality': 'fmri',
      'coil': '8-ch birdcage', 'fieldStrength': '3T'}
xutil.add_nifti(run2, 'image', '/Volumes/Data/NFRO1/Pre/1005/M2/SWR2.nii',
        other_md=md)