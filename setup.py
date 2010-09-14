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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""zope.app.publisher setup
"""
from setuptools import setup, find_packages

long_description = (open('README.txt').read() + '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.app.publisher',
      version = '3.10.2',
      url='http://pypi.python.org/pypi/zope.app.publisher/',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      classifiers = ['Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'Programming Language :: Python',
                     'Operating System :: OS Independent',
                     'Topic :: Internet :: WWW/HTTP',
                     'Framework :: Zope3',
                     ],
      description='Implementations and means for configuration of Zope 3-'
                  'style views and resources.',
      long_description=long_description,

      packages=find_packages('src'),
      package_dir={'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      include_package_data=True,
      install_requires=['setuptools',
                        'zope.browsermenu',
                        'zope.browserpage',
                        'zope.browserresource',
                        'zope.component',
                        'zope.configuration',
                        'zope.datetime',
                        'zope.interface',
                        'zope.location',
                        'zope.ptresource',
                        'zope.publisher>=3.12',
                        'zope.schema',
                        'zope.security',
                        'zope.componentvocabulary',
                        ],
      extras_require={
          'test': ['zope.testing',
                   'zope.app.testing',
                   'zope.app.zcmlfiles',
                   'zope.container>=3.9',
                   'zope.securitypolicy',
                   'zope.site',
                   'zope.login',
                   ],
          },

      zip_safe = False,
      )
