#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module is meant to provide more-useful interface functions to an XNAT 
server than currently provided by pyxnat."""

import os
import time
from ConfigParser import ConfigParser

try:
    import nibabel as nib
    use_nibabel = True
except ImportError:
    use_nibabel = False

from pyxnat import Interface
from pyxnat.core.resources import Project, Subject, Experiment, Scan
from pyxnat.core.errors import DatabaseError

ALLOWED_KEYS = {Subject: set(['group', 'src', 'pi_lastname',
                    'pi_firstname','dob', 'yob', 'age', 'gender',
                    'handedness', 'ses', 'education', 'educationDesc',
                    'race', 'ethnicity', 'weight', 'height',
                    'gestational_age','post_menstrual_age',
                    'birth_weight']),
                Project: set(['ID', 'secondary_ID', 'name',
                    'description', 'keywords', 'alias', 'pi_lastname',
                    'pi_firstname', 'note']),
                Experiment: set(['visit_id', 'date', 'ID', 'project',
                    'label', 'time', 'note', 'pi_firstname', 'pi_lastname',
                    'validation_method', 'validation_status',
                    'validation_date', 'validation_notes', 'subject_ID',
                    'subject_label', 'subject_project', 'scanner',
                    'operator', 'dcmAccessionNumber', 'dcmPatientId',
                    'dcmPatientName', 'session_type', 'modality',
                    'UID', 'coil', 'fieldStrength', 'marker',
                    'stabilization', 'studyType', 'patientID',
                    'patientName', 'stabilization', 'scan_start_time',
                    'injection_start_time', 'tracer_name',
                    'tracer_startTime', 'tracer_dose', 'tracer_sa',
                    'tracer_totalmass', 'tracer_intermediate',
                    'tracer_isotope', 'tracer_transmissions',
                    'tracer_transmissions_start']),
                Scan: set(['ID', 'type', 'UID', 'note', 'quality',
                    'condition', 'series_description', 'documentation',
                    'scanner', 'modality', 'frames', 'validation_method',
                    'validation_status', 'validation_date',
                    'validation_notes', 'coil', 'fieldStrength', 'marker',
                    'stabilization', 'orientation', 'scanTime',
                    'originalFileName', 'fileType', 'transaxialFOV',
                    'acqType', 'facility', 'numPlanes', 'numFrames',
                    'numGates', 'planeSeparation', 'binSize', 'dataType'])}

NIBABEL_TO_XNAT = {
'session_error': (lambda x: 'Good' if x == 0 else 'Error', 'validation_status'),
'dim': (lambda x: str(x[4]), 'frames'),
'datatype': (lambda x: str(x.dtype), 'dataType'),
'descrip': (lambda x: ' '.join(str(x).split()), 'series_description')
}

def xnat(cfg=os.path.join(os.path.expanduser('~'), '.xnat.cfg')):
    """Initialize and test xnat connection from a previously-stored cfg file

    Parameters
    ----------
    cfg: str
        Path to a stored interface configuration
        This is not from Interface.save_config but rather looks like this:
        [xnat]
        user: [your user name]
        password: [your password]
        server: [your xnat server]
        cache: [dir]

    Returns
    -------
    A valid Interface object to your XNAT system.

    This may throw an error from pyxnat.core.errors
    """

    cp = ConfigParser()
    with open(cfg) as f:
        cp.readfp(f)
    user = cp.get('xnat', 'user')
    password = cp.get('xnat', 'password')
    server = cp.get('xnat', 'server')
    cachedir = cp.get('xnat', 'cache')
    
    if '~' in cachedir:
        cachedir = os.path.expanduser(cachedir)
    
    xnat = Interface(server=server,
                    user=user,
                    password=password,
                    cachedir=cachedir)
    # Because the constructor doesn't test the connection, make sure 'admin' is 
    # in the list of users. Any errors are passed to the caller.
    if user not in xnat.manage.users():
        raise ValueError('This XNAT is weird.')
    xnat._memtimeout = 0.001
    return xnat

def project(xnat, name, proj_data={}):
    """ Create a new project/update project info
    
    Parameters
    ----------
    xnat: pyxnat.Interface object
        The connection to your xnat system
    name: str
        Project name
    proj_data: dict
        Project data you'd like to initialize 
    Returns
    -------
    pjt: Project object
        
    """
    pjt = _check_parent_and_get(xnat, xnat.select.project, name)
    if proj_data:
        succeeded, bad = _update_metadata(pjt, proj_data)
        if not succeeded:
            raise ValueError("Bad project keys: %s" % ' '.join(bad))
    return pjt

def subject(project, name, sub_data={}):
    """ Create a new subject/Update subject info
    
    WARNING: Previously stored data will be overwritten

    Parameters
    ----------
    project: pyxnat.Interface.project()
        An established project
    name: str
        Subject identifier
    data: dict
        Demographic data to set in xnat
        See 'xnat:subjectData' at
        http://docs.xnat.org/XNAT+REST+XML+Path+Shortcuts
        for allowed keys

    Returns
    -------
    sub: a valid subject object
    """
    sub = _check_parent_and_get(project, project.subject, name)
    if sub_data:
        succeeded, bad = _update_metadata(sub, sub_data)
        if not succeeded:
            raise ValueError("Bad subject data keys: %s" % ' '.join(bad))
    return sub

def experiment(subject, name, exp_data={}):
    """ Create/Update a subject's experiment
    
    Parameters
    ----------
    subject: Subject object
        The subject to which you want to create/update the experiment
    name: str
        Experiment string name
    exp_data: dict
        Experiment metadata to set in xnat
        See 'xnat:experimentData' at
        http://docs.xnat.org/XNAT+REST+XML+Path+Shortcuts
        for allowed keys
        
    Returns
    -------
    exp: a valid experiment object
    """
    exp = _check_parent_and_get(subject, subject.experiment, name)
    if exp_data:
        succeeded, bad = _update_metadata(exp, exp_data)
        if not succeeded:
            raise ValueError("Bad experiment data keys: %s" % ' '.join(bad))
    return exp
        
def scan(experiment, name, scan_data={}):
    """ Create/Update an experiment's scan
    
    Parameters
    ----------
    experiment: experiment object
        The experiment for which you want to create/update a scan
    name: str
        Scan string name
    scan_data: dict
        Scan metadata to set in xnat
        See 'xnat:imageScanData' at
        http://docs.xnat.org/XNAT+REST+XML+Path+Shortcuts
        for allowed keys
        
    Returns
    -------
    scan: a valid scan object
    """
    scan = _check_parent_and_get(experiment, experiment.scan, name)
    if scan_data:
        succeeded, bad = _update_metadata(scan, scan_data)
        if not succeeded:
            raise ValueError("Bad scan data keys: %s" % ' '.join(bad))
    return scan
    
def add_nifti(scan, res_name, fpath, file_name='image', other_md={}):
    """ Upload a nifti into a scan
    
    Parameters
    ----------
    scan: scan object
    res_name: str
        Name of the resource this file will be a child of
    file_name: str
        The name of the file in the string
    fpath: str
        Path on local machine of file to upload
    other_md: dict
        
    """
    res = resource(scan, res_name)
    md = {}
    if use_nibabel:
        try:
            img = nib.load(fpath)
            hdr = img.get_header()
        except IOError:
            raise IOError("%s doesn't exist on the filesystem." % fpath)
        except nib.spatialimages.ImageFileError:
            raise ValueError("%s doesn't appear to be a proper nifti1 image" 
                            % fpath)
        # map nib header keys to xnat metadata
        for k, t in NIBABEL_TO_XNAT.items():
            f = t[0]
            md[t[1]] = f(hdr[k])
        #  hard-code some variables
        md['validation_method'] = 'nibabel header check/pyxnat tools'
        md['validation_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
    md['note'] = 'uploaded with pyxnat tools'
    #  update md with passed arg
    md.update(other_md)
    #  send scan metadata 
    s, bk = _update_metadata(scan, md)
    #  Upload
    res.file(file_name).put(fpath)

def _update_metadata(xnat_obj, new_data={}):
    """ Update metadata for a xnat object

    Parameters
    ----------
    xnat_obj: any xnat object
        The object whose metadata you wish to update
    new_data: dict
        Data whose keys must match allowed keys

    Returns
    -------
    succeeded: bool
        That update worked
    bad_keys: seq
        If succeeded, empty, otherwise a sequence of the keys not accepted by
        xnat
    """
    if not xnat_obj.exists():
        raise ValueError("This object doesn't exist in xnat")
    succeeded, bad_keys = _key_check(type(xnat_obj), new_data.keys())
    if succeeded:
        #  do the mset
        xnat_obj.attrs.mset(new_data)
        #  TODO: check that the mset worked
#         for key, val in new_data.items():
#             good_update = xnat_obj.attrs.get(key) == val
#             if not good_update:
#                 #  TODO change to warning
#                 print("WARNING: %s wasn't updated" % key)
    return succeeded, bad_keys
        
def _check_parent_and_get(parent, creator_fn, name):
    """ Private method to check resource owner validity and create/return
    the new child 

    Parameters
    ----------
    parent: Some xnat object
        The owning object, i.e. the object directly owned the desired child
    creator_fn: fn
        function handle used to create new child
    name: str
        label for new child

    Returns
    -------
    child: valid xnat object guaranteed to exist in the xnat system
    """
    if hasattr(parent, 'exists'):
        if not parent.exists():
            raise ValueError("Parent %s doesn't exist" % parent)
    child = creator_fn(name)
    if not child.exists():
        child.create()
    #  This might fail, actually
    if not child.exists():
        msg = "Cannot create object (probably a privilege issue)"
        raise DatabaseError(msg)
    return child

def _key_check(check_type, keys):
    """ Private method to validate parameters before resource creation.

    Parameters
    ----------
    check_type: type
        resource type (call with something like (type(obj) )
    keys: iterable
        parameters to check
    Returns
    -------
    passed: bool
        True if keys match xnat parameters, False if not
    bad_keys: iterable
        keys the caller specified that xnat won't accept
    """
    if check_type not in ALLOWED_KEYS:
        raise NotImplementedError("Cannot currently check %s" % check_type)
    key_set = set(keys)
    passed = False
    bad_keys = []
    if ALLOWED_KEYS[check_type].issuperset(key_set):
        passed = True
    else:
        bad_keys.extend(key_set.difference(ALLOWED_KEYS[check_type]))
    return passed, bad_keys

