#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
import requests

import redcap
from xnat import util as xutil
from xnat.config import rc as rc_keys

XNAT_URL = 'http://masi.vuse.vanderbilt.edu:8078/xnat'


def user_by_email(interface, email):
    result = None
    users = interface.manage.users()
    for user in users:
        if interface.manage.users.email(user).lower() == email.lower():
            result = user
    return result


def search_dict_list_in(dl, key, value):
    result = filter(lambda x: value in x[key], dl)
    if len(result) < 1:
        raise ValueError("Empty search among the %s field." % key)
    return result[0]


def make_new_project(interface, project_data, lastname):
    print('#############')
    print("New project: %s" % lastname)
    p_data = search_dict_list_in(project_data, 'pi_name', lastname)
    last_up = lastname.upper()
    md = {}
    md['ID'] = last_up
    md['name'] = last_up
    md['secondary_ID'] = ''

    # transform pi name
    fname, lname = parse_pi_name(p_data['pi_name'])
    md['pi_firstname'] = fname
    md['pi_lastname'] = lname

    md['description'] = "All sessions acquired for Dr. %s" % lastname

    pi_email = p_data['pi_email']
    pi_user = user_by_email(interface, pi_email)
    if not pi_user:
        uname = pi_email.split('@')[0]
        while uname in interface.manage.users():
            uname = '%s%d' % (uname, random.randint(0, 9))
        upass = uname + ''.join([str(random.randint(0, 9)) for _ in range(10)])
        print "Creating user for %s %s with username %s ..." % (fname, lname, uname)
        register_user(uname, upass, fname, lname, pi_email)
        pi_user = user_by_email(interface, pi_email)

    print("Creating a project with the following metadata...")
    print '\n'.join(['%s:\t\t\t%s' % (k, v) for k, v in md.items()])

    new_prj = interface.select.project(last_up)
    if not new_prj.exists():
        new_prj.create()
    new_prj.attrs.mset(md)

    #  Add PI to project as owner
    print("Adding %s %s to project..." % (fname, lname))
    new_prj.add_user(pi_user, role='owner')


def register_user(login, upass, fname, lname, email):
    pl = {'xdat:user.login': login,
          'xdat:user.primary_password': upass,
          'xdat:user.firstname': fname,
          'xdat:user.lastname': lname,
          'xdat:user.email': email,
          'lab': 'NA',
          'comments': 'NA',
          'xdat:user.primary_password.encrypt': 'true'}
    r = requests.get(XNAT_URL + "/app/action/XDATRegisterUser", params=pl)
    r.raise_for_status()


def parse_pi_name(name):
    if ',' not in name:
        return '', ''
    parts = name.replace(' ', '').replace('.', '').split(',')
    last = parts[0]
    first = parts[1]
    return first, last


def get_lastnames(project_data):
    return list(set([parse_pi_name(x['pi_name'])[1] for x in project_data
        if parse_pi_name(x['pi_name'])[0]]))


if __name__ == '__main__':

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
    interface = xutil.xnat()

    """ Grab all existing project IDs """
    existing_projects = interface.select.projects().get('id')

    """ Get all transformed PI lastnames """
    lastnames = get_lastnames(project_data)

    projects_to_insert = []
    """ Find the project ids not currently in xnat """
    for lastname in lastnames:
        if lastname.upper() in existing_projects:
            # Project in xnat
            continue
        else:
            projects_to_insert.append(lastname)

    print("%s: %d project(s) to be imported..." % (time.strftime('%Y-%m-%d %H:%M'), len(projects_to_insert)))
    for lastname in projects_to_insert:
        make_new_project(interface, project_data, lastname)
