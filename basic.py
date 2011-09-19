import os

from pyxnat import Interface
import xnat_util as xutil


"""Below are basic accessors 

#  Initialize xnat
xnat = xutil.xnat()

#  Get your project
pjt = xutil.project(xnat, 'BTest')

#  Get your subject
sub = xutil.subject(pjt, 'sub1000')

#  Get your experiment
exp = xutil.experiment(sub, 'fmri_swr')

#  Get your scan
scan = xutil.scan(exp, 'mission_1')

#  Grab the right resource
res = xutil.resource(scan, 'image_nii_raw')
"""

""" These same methods create objects in XNAT if they don't exist and if you 
pass a dictionary, you can automatically fill out metadata """
xnat = xutil.xnat()

pjt_data = {'ID':'newBTest', 'description':'another project created by scott','pi_lastname':'Burns', 'pi_firstname':'Scott', 'note':'testing'}
new_prj = xutil.project(xnat, 'newBTest', pjt_data)

sub_data = {'gender': 'male', 'handedness': 'right', 'yob': '2000',
            'dob':'2000-11-11', 'ethnicity':'white'}
new_sub = xutil.subject(new_prj, '1234', sub_data)

exp_name = "fmri_swr"
exp_data = {'scanner': 'Phillips', 'operator': "Techname",
            'label': exp_name, 'pi_firstname': 'Scott',
            'pi_lastname': 'Burns', 'date': "2011-09-19", 'coil': '8ch-birdcage'}
new_exp = xutil.experiment(new_sub, exp_name, exp_data)

scan_name = 'mission_1'
scan_data = {'orientation':'horizontal', 'frames':'94', 'series_description':'sense'}
new_scan = xutil.scan(new_exp, 'scan_name', scan_data)

