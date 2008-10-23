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

from zope import component

from zope.publisher.browser import TestRequest

from zope.app.component.interfaces import ISite
from zope.app.publisher.browser.resource import Resource
from zope.app.publisher.browser.tests import support
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.traversing.browser.interfaces import IAbsoluteURL


class TestResource(support.SiteHandler, PlacelessSetup, unittest.TestCase):

    def testGlobal(self):
        req = TestRequest()
        r = Resource(req)
        req._vh_root = support.site
        r.__parent__ = support.site
        r.__name__ = 'foo'
        self.assertEquals(r(), 'http://127.0.0.1/@@/foo')
        r.__name__ = '++resource++foo'
        self.assertEquals(r(), 'http://127.0.0.1/@@/foo')

    def testGlobalInVirtualHost(self):
        req = TestRequest()
        req.setVirtualHostRoot(['x', 'y'])
        r = Resource(req)
        req._vh_root = support.site
        r.__parent__ = support.site
        r.__name__ = 'foo'
        self.assertEquals(r(), 'http://127.0.0.1/x/y/@@/foo')

    def testResourceUrl(self):
        # fake IAbsoluteURL adapter
        def resourceBase(site, request):
            return 'http://cdn.example.com'
        component.provideAdapter(resourceBase, (ISite, TestRequest), 
            IAbsoluteURL, 'resource')

        req = TestRequest()
        r = Resource(req)
        req._vh_root = support.site
        r.__parent__ = support.site
        r.__name__ = 'foo'
        self.assertEquals(r(), 'http://cdn.example.com/@@/foo')


def test_suite():
    return unittest.makeSuite(TestResource)

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
