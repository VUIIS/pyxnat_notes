#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
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

    api_key = rc_keys['vuiis-newapp']
    """ Initialize redcap project with url and key"""
    rc_project = redcap.Project('https://redcap.vanderbilt.edu/api/', api_key)
    # request_number --> project_number
    # project_title
    # project_description --> description
    # email --> pi_email
    # principal_investigator --> pi_name
    # orig_projectid
    fields_of_interest = ['project_number', 'project_title', 'description',
        'pi_email', 'orig_projectid', 'pi_name']
    project_data = rc_project.export_records(fields=fields_of_interest)

    """ Initialize the XNAT interface """
    admin_xnat = xutil.xnat()

    """ Grab all existing project IDs """
    existing_projects = admin_xnat.select.projects().get('id')

    """ Grab all projects (with proper request codes) in redcap """
    p54 = [(p['project_number'], p['orig_projectid']) for p in project_data]

    projects_to_insert = []
    """ Find the project ids not currently in xnat """
    for p5, p4 in p54:
        if p4 in existing_projects or p5 in existing_projects:
            # Project in xnat
            continue
        if p4: # There is a four digit code
            projects_to_insert.append((p4, 'orig_projectid'))
        elif p5:
            projects_to_insert.append((p5, 'project_number'))
        else:
            # Blank for both, don't care about this row
            pass

    pis = []
    print("%s: %d project(s) to be imported..." % (time.strftime('%Y-%m-%d %H:%M'), len(projects_to_insert)))
    for project_id, id_key in projects_to_insert:

        print('#############')
        print("New project: %s" % project_id)
        p_data = search_dict_list(project_data, id_key, project_id)
        md = {}
        md['ID'] = project_id
        md['name'] = p_data['project_title'][0:255]
        md['secondary_ID'] = p_data['project_title'][0:23]

        # transform pi name
        pi = p_data['pi_name'].lower()
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

        md['description'] = unicode(p_data['description'])

        pi_email = p_data['pi_email']
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

        #  Set to automatically bypass pre-archive
        new_prj.set_prearchive_code('4')
        print('#############')
        print
