import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.publisher',
      version='0.1',
      url='http://svn.zope.org/zope.app.publisher',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

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
