##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for Resource

$Id: test_resource.py,v 1.5 2003/08/16 00:43:51 srichter Exp $
"""
import unittest
from zope.app.context import ContextWrapper
from zope.app.publisher.browser.resource import Resource
from zope.component.interfaces import IResourceService
from zope.interface import implements
from zope.publisher.browser import TestRequest

class Service:
    implements(IResourceService)

class TestResource(unittest.TestCase):

    def testGlobal(self):
        req = TestRequest()
        r = ContextWrapper(Resource(req), Service(), name="foo")
        self.assertEquals(r(), '/@@/foo')
        r = ContextWrapper(Resource(req), Service(), name="++resource++foo")
        self.assertEquals(r(), '/@@/foo')

    def testGlobalWithSkin(self):
        req = TestRequest()
        req._presentation_skin = 'bar'
        r = ContextWrapper(Resource(req), Service(), name="foo")
        self.assertEquals(r(), '/++skin++bar/@@/foo')

    def testGlobalInVirtualHost(self):
        req = TestRequest()
        req.setVirtualHostRoot(['x', 'y'])
        r = ContextWrapper(Resource(req), Service(), name="foo")
        self.assertEquals(r(), '/x/y/@@/foo')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestResource))
    return suite


if __name__ == '__main__':
    unittest.main()
