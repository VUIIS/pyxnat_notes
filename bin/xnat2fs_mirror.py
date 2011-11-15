#!/usr/bin/env python
# -*- coding: utf-8 -*-
__license__ = 'BSD 3-Clause'

""" This script can be set up as a cron job to mirror an XNAT project into a 
local filesystem """

import os
import redcap

from xnat.util import xnat
from xnat.config import rc as rc_keys
from xnat.mail import mail

TO = ['scott.s.burns@vanderbilt.edu']

#  Top level directory for data, subjects go under this
subjects_dir = '/fs0/New_Server/%(study)s/MR_Raw/%(id)s'

PROJECT_DATA = {'RCV':{'key':'participant_id', 'scan_key': 'scan_num',
                        'config_key': 'rc', 'code':'2096'}}

def arguments():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    #  Add arguments
    ap.add_argument('project')
    ap.add_argument('--force')
    
    return ap.parse_args()

def xnatID_to_fsID(xnatID, redcap_project, query_key, unique_key):
    """ We want to take the scan ID from xnat and map it to our labeling system """
    q = redcap.Query('scan_num', {'eq': xnatID})
    d = redcap_project.filter(q, output_fields=[unique_key])
    if len(d) != 1:
        raise ValueError("more than one subject for this search!")
    return d[0][unique_key]

# def dcm_to_nii(dcm, nii):
#     import nibabel as nib
#     if not os.path.isfile(dcm):
#         raise ValueError("dcm file passed doesn't exist")
#     

def mirror(sub_label, exp, top_dir, convert_to_nii=False, nii_top_dir=None):
    """ Mirror all of the scans into top_dir from this experiment 
    
    I'd like to preserve filenaming scheme that getstudy outputs:
    [PI]_ScanID_Scan#_SubScan#_ScanType.DCM"""

    if convert_to_nii and nii_top_dir:
        raise NotImplementedError

    #  We want all scans > 100, 0 is ref    
    good_scans = filter(lambda x: int(x) > 100, exp.scans().get())
    all_new_files = []
    for scan in good_scans:
        scan_num = '%02d' % (int(scan) / 100)
        subscan_num = '%02d' % (int(scan) % 100)
        #  Get the scan object
        xscan = exp.scan(scan)
        scan_type = xscan.attrs.get('type').replace(' ', '_')
        all_res = xscan.resources().get()
        #  Until we understand why we're getting two DCM objects,
        #  We want the resource with the largest dcm
        all_xres = [xscan.resource(res) for res in all_res]
        all_fsize = [int(xres.file(xres.files().get()[0]).size()) for xres in all_xres]
        fsize_sort = sorted(all_fsize, reverse=True)
        xres_ind = all_fsize.index(fsize_sort[0])
        xres = all_xres[xres_ind]
        #  xres is now the resource with the largest file
        files = xres.files().get()
        if len(files) > 1:
            print("Warning, more than one file...using first")
        xfile = xres.file(files[0])
        new_fname = os.path.join(top_dir, '_'.join([sub_label, scan_num, 
                        subscan_num, scan_type])+'.DCM')
        new_f = xfile.get_copy(new_fname)
        all_new_files.append(new_f)
    return all_new_files            

if __name__ == '__main__':

    args = arguments()

    project_info = PROJECT_DATA[args.project]

    API_KEY = rc_keys[project_info['config_key']]

    rc_proj = redcap.Project('https://redcap.vanderbilt.edu/api/', API_KEY)

    x = xnat()
    #  Grab your project
    xproj = x.select.project(project_info['code'])
    #  This returns only the string
    all_subs = xproj.subjects().get()
    email_body = ''
    for sub in all_subs:
        #  This returns the actual subject object
        xsub = xproj.subject(sub)
        #  This grant has only one experiment per subject
        exps = xsub.experiments().get()
        xexp = xsub.experiment(exps[0])
        #  xexp.label() is the scanid that Cutting Lab uses
        our_id = xnatID_to_fsID(xexp.label(), rc_proj,
                    project_info['scan_key'], project_info['key'])
        top_dir = subjects_dir % {'study': args.project, 'id': our_id}
        dcm_dir = os.path.join(top_dir,'DICOM')
        if not os.path.isdir(dcm_dir):
            #  Then we need to mirror
            try:
                os.makedirs(dcm_dir)
            except OSError:
                #  TODO Fix
                #  We probably are using --force
                pass     
            new_files = mirror(xsub.label(), xexp, dcm_dir)
            email_body += "For %s, imported these files..." % our_id
            email_body += '\n'.join(new_files)
        else:
            #  Skip to next subject
            pass
    if email_body:
        email_subject = "%s: Automatic Import Report" % args.project
        mail(TO, email_subject, email_body)
