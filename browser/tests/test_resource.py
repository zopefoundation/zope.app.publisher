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

$Id: test_resource.py,v 1.1 2003/04/15 12:24:33 alga Exp $
"""

import unittest
from zope.publisher.browser import TestRequest
from zope.proxy.context import ContextWrapper

class TestResource(unittest.TestCase):

    def testGlobal(self):
        from zope.app.publisher.browser.resource import Resource
        req = TestRequest()
        r = ContextWrapper(Resource(req), None, name="foo")
        self.assertEquals(r(), '/@@/foo')
        r = ContextWrapper(Resource(req), None, name="++resource++foo")
        self.assertEquals(r(), '/@@/foo')

    def testGlobalWithSkin(self):
        from zope.app.publisher.browser.resource import Resource
        req = TestRequest()
        req._presentation_skin = 'bar'
        r = ContextWrapper(Resource(req), None, name="foo")
        self.assertEquals(r(), '/++skin++bar/@@/foo')

    def testGlobalInVirtualHost(self):
        from zope.app.publisher.browser.resource import Resource
        req = TestRequest()
        req.setApplicationNames(['x', 'y'])
        r = ContextWrapper(Resource(req), None, name="foo")
        self.assertEquals(r(), '/x/y/@@/foo')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestResource))
    return suite


if __name__ == '__main__':
    unittest.main()
