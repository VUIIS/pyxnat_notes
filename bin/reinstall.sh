#!/bin/sh

#  uninstall
python setup.py develop -u
#  clean build dirs
python setup.py clean
#  install
python setup.py install

