#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xnat_util as xutil

#  Init
xnat = xutil.load_xnat()

pjt = xnat.select.project('BTest')

#  batch sub creation
subs = ['sub%d' % i for i in range(1000, 1002)]
sub_data = [{'gender':'M'},
            {'gender':'F'}
            ]
new_subs = []
for sub_n, sub_d in zip(subs, sub_data):
    n_sub = xutil.new_subject(pjt, sub_n, sub_d)
    new_subs.append(n_sub)
# 
# xsub = pjt.subject(sub)
# if not xsub.exists():
#     xsub.create()
# 
# #  experiment name
# exp_name = 'fmri'
# exp = xsub.experiment(exp_name)
# 
# #  first scan
# scan_name = 'run1'
# run = exp.scan(scan_name)
# 
# #  make a new resource
# res_name = 'mr_data'
# res = run.resource(res_name)
# 
# # now do the upload
# #  This is the image name in xnat
# imname = 'imag1.nii'
# #  A local nifti file that we want to upload
# nii = '/Volumes/Data/NFRO1/Pre/1005/M1/SWR1.nii'
# res.file(imname).put(nii)
