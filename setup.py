#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <phil@canary.md>
# date: 2014/12/02
# copy: (C) Copyright 2014-EOT Canary Health, Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import os, sys, setuptools
from setuptools import setup, find_packages

# require python 2.7+
if sys.hexversion < 0x02070000:
  raise RuntimeError('This package requires python 2.7 or better')

heredir = os.path.abspath(os.path.dirname(__file__))
def read(*parts, **kw):
  try:    return open(os.path.join(heredir, *parts)).read()
  except: return kw.get('default', '')

test_dependencies = [
  'nose                 >= 1.3.0',
  'coverage             >= 3.5.3',
]

dependencies = [
  'six                  >= 1.4.1',
  'requests             >= 2.2.1',
  'aadict               >= 0.2.2',
  'morph                >= 0.1.2',
  'asset                >= 0.6.3',
]

entrypoints = {
  'console_scripts': [
    'canarymd           = canarymd.cli:main',
  ],
}

classifiers = [
  'Development Status :: 3 - Alpha',
  #'Development Status :: 4 - Beta',
  #'Development Status :: 5 - Production/Stable',
  #'Development Status :: 6 - Mature',
  #'Development Status :: 7 - Inactive',
  'Environment :: Console',
  'Environment :: Web Environment',
  'Framework :: Pyramid',
  'Intended Audience :: Developers',
  'Intended Audience :: Healthcare Industry',
  'Intended Audience :: Science/Research',
  'License :: OSI Approved :: MIT License',
  'Natural Language :: English',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Programming Language :: Python :: 2.7',
  'Programming Language :: Python :: 2 :: Only',
  'Programming Language :: Python :: 3',
  'Topic :: Internet :: WWW/HTTP',
  'Topic :: Scientific/Engineering :: Bio-Informatics',
  'Topic :: Scientific/Engineering :: Medical Science Apps.',
  'Topic :: Utilities',
]

setup(
  name                  = 'canarymd',
  version               = read('VERSION.txt', default='0.0.1').strip(),
  description           = 'A python client library that allows easy integration with Canary',
  long_description      = read('README.rst'),
  classifiers           = classifiers,
  author                = 'Philip J Grabner, Canary Health Inc',
  author_email          = 'oss@canary.md',
  url                   = 'http://github.com/canaryhealth/canarymd-python',
  keywords              = 'canary health python client library rest',
  packages              = setuptools.find_packages(),
  include_package_data  = True,
  zip_safe              = True,
  install_requires      = dependencies,
  tests_require         = test_dependencies,
  test_suite            = 'canarymd',
  entry_points          = entrypoints,
  license               = 'MIT (http://opensource.org/licenses/MIT)',
)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
