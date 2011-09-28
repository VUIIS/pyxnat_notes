#!/usr/bin/env python
# -*- coding: utf-8 -*-

import .util

class XNAT(object):
    """ This is a simple wrapper for many of the above methods """
    
    def __init__(self, interface):
        """ Constructor 

        Parameters
        ----------
        interface: pyxnat.interface
            The interface object to you xnat system
        """
        self.xnat = interface
        
        self.projs = xnat.select.projects().get()
        self.proj = None
        
        self.subs = None
        self.sub = None
        
        self.exps = None
        self.exp = None
        
        self.scans = None
        self.scan = None
        
        self.ress = None
        self.res = None
        
        self.files = None
        self.file = None
    
    def _set_current(field, label, group, lower_fn, lower_field):
        """ Private
        
        Set a given attribute to a new value
        
        Parameters
        ----------
        field: attribute
            An attribute of self
        label: str
            To-be-current label for field
        group: iter
            Group in which label must exist
        """
        within = label in group
        if not within:
            raise ValueError("%s doesn't exist, try creating it first" % label)
        else:
            lower_field = None
            field = label
            lower_field = lower_fn().get()
    
    def set_project(self, proj_label):
        """ Set the current project
        
        Parameters
        ----------
        proj_label: str
            Project name
        """
        if proj_label not in self.projs:
            msg = "Cannot set %s as current project, it doesn't exist"
            print(msg % proj_label)
        else:
            self.proj = xnat.select.project(proj_label)
            sub_ids = self.proj.subjects().get()
            self.subs = None
            self.subs = [self.proj.subject(id).label() for id in sub_ids]
            
            #  Reset everything below
            self.sub = None
            self.exps = None
            self.exp = None            
            self.scans = None
            self.scan = None
            self.ress = None
            self.res = None
            self.files = None
            self.file = None
            
