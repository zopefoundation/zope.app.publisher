##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""zope.app.publisher setup
"""
from setuptools import setup, find_packages, Extension

setup(name='zope.app.publisher',
      version = '3.4.0b2',
      url='http://pypi.python.org/pypi/zope.app.publisher',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      classifiers = ['Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'Programming Language :: Python',
                     'Operating System :: OS Independent',
                     'Topic :: Internet :: WWW/HTTP',
                     'Framework :: Zope3',
                     ],

      packages=find_packages('src'),
      package_dir={'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      include_package_data=True,
      install_requires=['setuptools',
                        'zope.app.component',
                        'zope.app.container',
                        'zope.app.pagetemplate',
                        'zope.app.publication',
                        'zope.component',
                        'zope.configuration',
                        'zope.contenttype',
                        'zope.datetime',
                        'zope.deferredimport',
                        'zope.deprecation',
                        'zope.i18n',
                        'zope.interface',
                        'zope.location',
                        'zope.pagetemplate',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.traversing',
                        ],
      extras_require={
          'test': ['zope.testing',
                   'zope.app.testing',
                   'zope.app.securitypolicy',
                   'zope.app.zcmlfiles'],
          'back35': ['zope.app.skins',
                     'zope.app.layers'],
          },

      zip_safe = False,
      )
