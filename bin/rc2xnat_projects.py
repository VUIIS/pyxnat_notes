#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
from urllib import quote, urlopen

import redcap
from xnat import util as xutil
from xnat.config import rc as rc_keys

def user_by_email(interface, email):
    result = None
    users = interface.manage.users();
    for user in users:
        if interface.manage.users.email(user).lower() == email.lower(): 
            result = user
    return result

def search_dict_list(dl, key, value):
    result = filter(lambda x: x[key] == value, dl)
    if len(result) != 1:
        raise ValueError("Collision among the %s field." % key)
    return result[0]


if __name__ == '__main__':
    xnat_url = 'http://masi.vuse.vanderbilt.edu/xnat'

    api_key = rc_keys['vuiis-projectapp']
    """ Initialize redcap project with url and key"""
    rc_project = redcap.Project('https://redcap.vanderbilt.edu/api/', api_key)
    project_data = rc_project.export_records()
    
    """ Initialize the XNAT interface """
    admin_xnat = xutil.xnat()
    
    """ Grab all existing project IDs """
    existing_projects = admin_xnat.select.projects().get('id')
    
    """ Grab all projects (with proper request codes)
    in redcap """
    all_project_ids = [p['request_number'] for p in project_data if len(p['request_number']) > 0]
    
    """ Find the project ids not currently in xnat """
    projects_to_insert = list(set(all_project_ids) - set(existing_projects))
    
    
    pis = []
    print("%d project(s) to be imported..." % len(projects_to_insert))
    for project_id in projects_to_insert:
    
        print('#############')
        print("New project: %s" % project_id)
        p_data = search_dict_list(project_data, 'request_number', project_id)
        md = {}
        md['ID'] = project_id
        md['name'] = p_data['project_title'][0:255]
        md['secondary_ID'] = p_data['project_title'][0:23]
    
        # transform pi name
        pi = p_data['principal_investigator'].lower()
        pi = pi.replace('.', '')
        pi = pi.replace(',', '')
        pi_parts = [x.capitalize() for x in pi.split() if x not in ('dr', 'md', 'phd', 'ms')]
        if len(pi_parts) == 0:
            print("WARNING: cannot determine PI name for this project")
            md['pi_firstname'] = 'missing'
            md['pi_lastname'] = 'missing'                
        elif len(pi_parts) == 1:
            md['pi_firstname'] = pi_parts[0]
            md['pi_lastname'] = 'missing'
        elif len(pi_parts) > 1:  # Assume well formatted    
            md['pi_firstname'] = pi_parts[0]
            md['pi_lastname'] = pi_parts[-1]
        fname = md['pi_firstname']
        lname = md['pi_lastname']
    
        md['description'] = unicode(p_data['project_description'])
    
        pi_email = p_data['email']
        pi_user = user_by_email(admin_xnat, pi_email)
        if not pi_user:
            uname = fname + lname
            while uname in admin_xnat.manage.users():
                uname = '%s%d' % (uname, random.randint(0, 9))
            upass = uname + '37027'
            print "Creating user for %s %s..." % (fname, lname)
            url = xnat_url + "/app/action/XDATRegisterUser?xdat%3Auser.login="+quote(uname)+"&xdat%3Auser.primary_password="+quote(upass)+"&xdat%3Auser.primary_password="+quote(upass)+"&xdat%3Auser.firstname="+quote(fname)+"&xdat%3Auser.lastname="+quote(lname)+"&xdat%3Auser.email="+quote(pi_email)+"&lab=NA&comments=NA&xdat%3Auser.primary_password.encrypt=true"
            urlopen(url).read()
            pi_user = user_by_email(admin_xnat, pi_email)
    
        print("Creating a project with the following metadata...")
        print '\n'.join(['%s:\t\t\t%s' % (k, v) for k, v in md.items()])
    
        new_prj = admin_xnat.select.project(project_id)
        if not new_prj.exists():
            new_prj.create()
        new_prj.attrs.mset(md)
    
        #  Add PI to project as owner
        print("Adding %s %s to project..." % (fname, lname))
        new_prj.add_user(pi_user, role='owner')
        print('#############')
        print