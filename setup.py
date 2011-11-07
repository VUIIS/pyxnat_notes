#!/usr/bin/env python
# -*- coding: utf-8 -*-
__license__ = 'BSD 3-Clause'

import os
import xnat

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if __name__ == '__main__':

    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name='xnat_tools',
        maintainer='VUIIS CCI',
        maintainer_email='vuiis.cci@gmail.com',
        description="""Tools and utilties related to CCI's XNAT install""",
        license='BSD (3-clause)',
        url='http://github.com/vuiis/pyxnat_notes',
        version=xnat.__version__,
        download_url='http://github.com/vuiis/pyxnat_notes',
        packages=['xnat'],
        package_data={},
        requires=['pyxnat'],
        platforms='any',
        classifiers=(
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved',
                'Topic :: Software Development',
                'Topic :: Scientific/Engineering',
                'Operating System :: Microsoft :: Windows',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Operating System :: MacOS',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.7',)
        )
