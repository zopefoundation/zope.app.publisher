##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test 'xmlrpc' ZCML Namespace directives.

$Id$
"""
import unittest

from zope.configuration import xmlconfig
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.tests.views import IC, V1
from zope.component import getView, queryView, getDefaultViewName
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.proxy import ProxyFactory

from zope.component.tests.request import Request

from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest

from zope.app.publisher import xmlrpc
from zope.interface import implements


request = Request(IXMLRPCRequest)

class Ob:
    implements(IC)

ob = Ob()

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def testView(self):
        self.assertEqual(queryView(ob, 'test', request), None)
        context = xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        self.assertEqual(queryView(ob, 'test', request).__class__, V1)

    def testInterfaceProtectedView(self):
        context = xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = getView(ob, 'test2', request)
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        context = xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = getView(ob, 'test3', request)
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        context = xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = getView(ob, 'test4', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        context = xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = getView(ob, 'test5', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(ConfigurationError, xmlconfig.file,
                          "xmlrpc_error.zcml", xmlrpc.tests)

    def testDefaultView(self):
        context = xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        self.assertEqual(getDefaultViewName(ob, request), 'test')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
