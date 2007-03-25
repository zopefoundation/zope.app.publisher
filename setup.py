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
      install_requires=[
          'setuptools',
          'zope.component',
          'zope.interface',
          'zope.publisher',
          ],
      extras_require={
          'test': ['zope.testing', 'zope.app.testing'],
          },

      zip_safe = False,
      )
