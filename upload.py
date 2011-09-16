#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xnat_util as xutil

#  Initialize XNAT
xnat = xutil.load_xnat()

#  Subjects belong to a project, so grab the project you'd like to put them in
pjt = xnat.select.project('BTest')

#  Experiments belong to a subject, so get a subject
sub = xutil.subject(pjt, 'sub1000')

exp_name = 'fmri'
exp = xsub.experiment(exp_name)

#  first scan
scan_name = 'run1'
run = exp.scan(scan_name)

#  make a new resource
res_name = 'mr_data'
res = run.resource(res_name)

# now do the upload
#  This is the image name in xnat
imname = 'imag1.nii'
#  A local nifti file that we want to upload
nii = '/Volumes/Data/NFRO1/Pre/1005/M1/SWR1.nii'
res.file(imname).put(nii)
