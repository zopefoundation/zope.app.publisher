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
# This package is developed by the Zope Toolkit project, documented here:
# https://zopetoolkit.readthedocs.io
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""zope.app.publisher setup
"""
from setuptools import setup


version = '6.0'


def _read(fname):
    with open(fname) as f:
        return f.read()


long_description = (_read('README.rst') + '\n\n' +
                    _read('CHANGES.rst'))

tests_require = [
    'zope.app.appsetup',
    'zope.app.authentication',
    'zope.app.basicskin >= 4.0.0',
    'zope.app.container >= 4.0.0',
    'zope.app.form >= 5.0.0',
    'zope.app.publisher',
    'zope.app.publication',
    'zope.app.rotterdam >= 4.0.0',
    'zope.app.schema >= 4.0.0',
    'zope.app.wsgi',

    'zope.browserpage',
    'zope.browserresource',
    'zope.container',
    'zope.deferredimport',
    'zope.formlib',
    'zope.login',
    'zope.principalannotation',
    'zope.principalregistry',
    'zope.publisher',
    'zope.securitypolicy',
    'zope.testbrowser >= 5.2',
    'zope.testing',
    'zope.testrunner >= 6.4',
    'zope.traversing >= 4.1.0',

    'webtest',
]

setup(name='zope.app.publisher',
      version=version,
      url='https://github.com/zopefoundation/zope.app.publisher/',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.dev',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope :: 3',
      ],
      description='Implementations and means for configuration of Zope 3-'
                  'style views and resources.',
      long_description=long_description,
      license='ZPL-2.1',
      include_package_data=True,
      python_requires='>=3.9',
      install_requires=[
          'setuptools',
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
          'test': tests_require,
          'testing': 'zope.app.wsgi',
      },
      tests_require=tests_require,
      zip_safe=False,
      )
