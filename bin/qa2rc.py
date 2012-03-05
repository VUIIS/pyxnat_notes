#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Scott Burns <scott.s.burns@gmail.com>'
__license__ = 'BSD 3-Clause'

import sys, os

if __name__ == '__main__':
    try:
        API_KEY = sys.argv[1]
        json_path = sys.argv[2]
    except IndexError:
        print("ERROR: python qa2rc.py api_key path/to/json.txt")
        sys.exit(1)

