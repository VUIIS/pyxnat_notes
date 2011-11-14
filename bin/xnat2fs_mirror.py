#!/usr/bin/env python
# -*- coding: utf-8 -*-
__license__ = 'BSD 3-Clause'

""" This script can be set up as a cron job to mirror an XNAT project into a 
local filesystem """

import os
import redcap

from xnat.util import xnat
from xnat.config import rc as rc_keys
"""
GLOBALS
"""
#  Xnat project ID
project_code = '2096'
#  Top level directory for data, subjects go under this
subjects_dir = '/fs0/New_Server/RCV/MR_Raw/'
#  Redcap project name
"""  In your .vuiisxnat.cfg file, make an 'rc' section if it doesn't already 
exist. The key you specify here should be in your 'rc' section """
redcap_project = 'rc'
API_KEY = rc_keys[redcap_project]

rc_proj = redcap.Project('https://redcap.vanderbilt.edu/api/', API_KEY)

def xnatID_to_fsID(xnatID):
    """ We want to take the scan ID from xnat and map it to our BEHAVID_SCANID
    labeling system """
    q = redcap.Query('scan_num', {'eq': xnatID})
    d = rc_proj.filter(q, output_fields=['participant_id'])
    if len(d) != 1:
        raise ValueError("more than one subject for this scan_num!")
    return d[0]['participant_id']

def mirror(sub_label, exp, top_dir):
    """ Mirror all of the scans into top_dir from this experiment 
    I'd like to preserve filenames that getstudy outputs:
    [PI]_ScanID_Scan#_SubScan#_WIP???_ScanType_Sense.DCM"""
    #  We want all scans > 100, 0 is ref
    good_scans = filter(lambda x: int(x) > 100, exp.scans().get())
    for scan in good_scans:
        scan_num = '%02d' % (int(scan) / 100)
        subscan_num = '%02d' % (int(scan) % 100)
        #  Get the scan object
        xscan = exp.scan(scan)
        scan_type = xscan.attrs.get('type').replace(' ', '_')
        res = xcan.resources().get()
        if len(res) > 1:
            print("Warning, mroe than one resource...using first")
        xres = xscan.resource(res[0])
        files = xres.files().get()
        if len(files) > 1:
            print("Warning, more than one file...using first")
        xfile = xres.file(files[0])
        new_fname = os.path.join(top_dir, '_'.join([sub_label, scan_num, 
                        subscan_num, scan_type])+'.DCM')
        print("Downloading file to %s" % new_fname)
        xfile.get_copy(new_fname)

if __name__ == '__main__':
    x = xnat()
    #  Grab your project
    xproj = x.select.project(project_code)
    #  This returns only the string
    all_subs = xproj.subjects().get()
    for sub in all_subs:
        #  This returns the actual subject object
        xsub = xproj.subject(sub)
        #  This grant has only one experiment per subject
        exps = xsub.experiments().get()
        xexp = xsub.experiment(exps[0])
        #  xexp.label() is the scanid that Cutting Lab uses
        our_id = xnatID_to_fsID(xexp.label())
        dcm_dir = os.path.join(subjects_dir, our_id, 'DICOM')
        if not os.path.isdir(dcm_dir):
            #  Then we need to mirror
            os.makedirs(dcm_dir)
            mirror(xsub.label(), xexp, dcm_dir)
        else:
            #  Skip to next subject
            pass