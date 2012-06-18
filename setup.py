##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

long_description = (open('README.txt').read() + '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.app.publisher',
      version = '3.8.5',
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
                        'zope.component>=3.7.0',
                        'zope.configuration',
                        'zope.container',
                        'zope.contenttype',
                        'zope.datetime',
                        'zope.i18n',
                        'zope.interface',
                        'zope.location',
                        'zope.pagetemplate>=3.5.0',
                        'zope.publisher>=3.8.0',
                        'zope.schema',
                        'zope.site',
                        'zope.security',
                        'zope.traversing>3.7.0',
                        'zope.componentvocabulary',
                        'zope.browser',
                        'zope.app.pagetemplate',
                        ],
      extras_require={
          'test': ['zope.testing',
                   'zope.app.testing',
                   'zope.app.securitypolicy',
                   'zope.app.zcmlfiles',
                   'zope.site'],
          },

      zip_safe = False,
      )
