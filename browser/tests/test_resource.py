##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unit tests for Resource

$Id$
"""
import unittest

from zope.component.service import serviceManager
from zope.interface import implements
from zope.publisher.browser import TestRequest

from zope.app.component.hooks import setSite
from zope.app.publisher.browser.resource import Resource
from zope.app.site.interfaces import ISite
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.interfaces import IContainmentRoot

class Site:
    implements(ISite, IContainmentRoot)

    def getSiteManager(self):
        return serviceManager

site = Site()

class TestResource(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestResource, self).setUp()
        setSite(site)

    def tearDown(self):
        setSite()
        super(TestResource, self).tearDown()

    def testGlobal(self):
        req = TestRequest()
        r = Resource(req)
        req._vh_root = site
        r.__parent__ = site
        r.__name__ = 'foo'
        self.assertEquals(r(), 'http://127.0.0.1/@@/foo')
        r.__name__ = '++resource++foo'
        self.assertEquals(r(), 'http://127.0.0.1/@@/foo')

    def testGlobalInVirtualHost(self):
        req = TestRequest()
        req.setVirtualHostRoot(['x', 'y'])
        r = Resource(req)
        req._vh_root = site
        r.__parent__ = site
        r.__name__ = 'foo'
        self.assertEquals(r(), 'http://127.0.0.1/x/y/@@/foo')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestResource))
    return suite


if __name__ == '__main__':
    unittest.main()
