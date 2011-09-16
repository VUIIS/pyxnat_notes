#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xnat_util as xutil

xnat = xutil.load_xnat()

proj_name = 'new_project_burns'
proj_data = {'ID':'newBTest', 'description':'another project created by scott'
, 'pi_lastname':'Burns', 'pi_firstname':'Scott', 'note':'testing'}

new_pjt = xutil.project(xnat, proj_name, proj_data)

