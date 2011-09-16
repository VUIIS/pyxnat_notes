#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import xnat_util as xutil

class UtilityFunctionTests(unittest.TestCase):
    """ Test XNAT Utility Functions """
    
    def setUp(self):
        """ Init xnat"""
        self.xnat = xutil.load_xnat()
        self.pjt = self.xnat.select.project('BTest')
        self.sub = self.pjt.subject('sub1000')
        
    def tearDown(self):
        """ Nothing to do? """
        pass
        
    def test_key_check_bad_type(self):
        """ Test _key_check for not-implemented types """
        bad_args = ['asdfjkl;', []]
        self.assertRaises(NotImplementedError, xutil._key_check, *bad_args)

