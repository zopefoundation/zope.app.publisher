##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
$Id$
"""

import os
from unittest import TestCase, main, makeSuite

from zope.exceptions import NotFoundError
from zope.proxy import isProxy, removeAllProxies
from zope.publisher.browser import TestRequest
from zope.security.checker import NamesChecker, ProxyFactory
from zope.interface import implements

from zope.app import zapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.publisher.browser.directoryresource import \
     DirectoryResourceFactory
from zope.app.container.contained import Contained
from zope.app.publisher.browser.fileresource import FileResource
from zope.app.publisher.browser.pagetemplateresource import \
     PageTemplateResource
import zope.app.publisher.browser.tests as p
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.site.interfaces import ISite

test_directory = os.path.split(p.__file__)[0]

checker = NamesChecker(
    ('get', '__getitem__', 'request', 'publishTraverse')
    )

class Site:
    implements(ISite, IContainmentRoot)

class Ob(Contained): pass

site = Site()
ob = Ob()

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()

    def testNotFound(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        resource = DirectoryResourceFactory(path, checker)(request)
        self.assertRaises(NotFoundError, resource.publishTraverse,
                          resource.request, 'doesnotexist')
        self.assertRaises(NotFoundError, resource.get, 'doesnotexist')

    def testGetitem(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        resource = DirectoryResourceFactory(path, checker)(request)
        self.assertRaises(KeyError, resource.__getitem__, 'doesnotexist')
        file = resource['test.txt']

    def testProxy(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        resource = DirectoryResourceFactory(path, checker)(request)
        file = ProxyFactory(resource['test.txt'])
        self.assert_(isProxy(file))

    def testURL(self):
        request = TestRequest()
        request._vh_root = site
        path = os.path.join(test_directory, 'testfiles')
        files = DirectoryResourceFactory(path, checker)(request)
        files.__parent__ = site
        files.__name__ = 'test_files'
        file = files['test.gif']
        self.assertEquals(file(), 'http://127.0.0.1/@@/test_files/test.gif')

    def testURL2Level(self):
        request = TestRequest()
        request._vh_root = site
        ob.__parent__ = site
        ob.__name__ = 'ob'
        path = os.path.join(test_directory, 'testfiles')
        files = DirectoryResourceFactory(path, checker)(request)
        files.__parent__ = ob
        files.__name__ = 'test_files'
        file = files['test.gif']
        self.assertEquals(file(), 'http://127.0.0.1/@@/test_files/test.gif')

    def testCorrectFactories(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        resource = DirectoryResourceFactory(path, checker)(request)

        image = resource['test.gif']
        self.assert_(isinstance(removeAllProxies(image), FileResource))
        template = resource['test.pt']
        self.assert_(isinstance(removeAllProxies(template), PageTemplateResource))
        file = resource['test.txt']
        self.assert_(isinstance(removeAllProxies(file), FileResource))

def test_suite():
    return makeSuite(Test)

if __name__ == '__main__':
    main(defaultTest='test_suite')
