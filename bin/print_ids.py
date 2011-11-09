#!/usr/bin/env python
# -*- coding: utf-8 -*-


from xnat import util

if __name__ == '__main__':
    x = util.xnat()
    
    all_projs = x.select.projects().get()
    
    print('\n'.join(all_projs))