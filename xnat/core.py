#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import util


class XNAT(object):
    """ This is a simple wrapper for many of the above methods """

    def __init__(self, interface=None, cfg=None):
        """ Constructor

        Parameters
        ----------
        interface: pyxnat.interface
            The interface object to you xnat system
        """
        if interface:
            self.xnat = interface
        else:
            if not cfg:
                good_cfg = os.path.join(os.path.expanduser('~'), '.xnat.cfg')
            else:
                good_cfg = cfg
            self.xnat = util.xnat(good_cfg)

        self.projs = self.xnat.select.projects().get()
        self.proj = None

        self.subs = None
        self.sub = None

        self.all_exps = None
        self.exps = None
        self.exp = None

        self.scans = None
        self.scan = None

        self.ress = None
        self.res = None

        self.files = None
        self.file = None

    def set_project(self, project_label):
        """ Set the current project

        Parameters
        ----------
        project_label: str
            Project name
        """
        if project_label not in self.projs:
            msg = "Cannot set %s as current project, it doesn't exist"
            raise ValueError(msg % project_label)
        else:
            self.proj = self.xnat.select.project(project_label)

            # Reset subs and get new subjects from project
            self.subs = None
            self.subs = self.proj.subjects().get('label')
            self.sub = None

            #  Reset all children
            ancestors = (self.exps, self.exp, self.scans, self.scan, self.ress,
                            self.res, self.files, self.file)
            for anc in ancestors:
                anc = None

    def set_subject(self, subject_label):
        """ Set the current subject

        Parameters
        ----------
        subject_label: str
            subject name
        """
        if subject_label not in self.subs:
            msg = "Cannot set %s as current subject, it doesn't exist"
            raise ValueError(msg % subject_label)
        self.sub = self.proj.subject(subject_label)

        # Reset exps and get new experiments from subject
        self.exps = None
        self.exps = self.sub.experiments().get('label')
        self.exp = None

        #  Reset all children
        ancestors = (self.scans, self.scan, self.ress, self.res,
                        self.files, self.file)
        for anc in ancestors:
            anc = None

    def set_experiment(self, exp_label):
        """ Set the current experiment

        Parameters
        ----------
        exp_label: str
            experiment label
        """
        if exp_label not in self.exps:
            msg = "Cannot set %s as current experiment, doesn't exist"
            raise ValueError(msg % exp_label)
        self.exp = self.sub.experiment(exp_label)

        # Reset scans, get new ones from experiment
        self.scans = None
        self.scans = self.exp.scans().get('label')
        self.scan = None

        #  Reset all children
        ancestors = (self.ress, self.res, self.files, self.file)
        for anc in ancestors:
            anc = None
        
    def set_scan(self, scan_label):
        """ Set the current scan

        Parameters
        ----------
        scan_label: str
            scan label
        """
        if exp_label not in self.exps:
            msg = "Cannot set %s as current scan, doesn't exist"
            raise ValueError(msg % exp_label)
        self.exp = self.sub.scan(exp_label)

        # Reset resources, get new ones from scan
        self.ress = None
        self.ress = self.exp.resources().get('label')
        self.res = None

        #  Reset all children
        ancestors = (self.files, self.file)
        for anc in ancestors:
            anc = None

