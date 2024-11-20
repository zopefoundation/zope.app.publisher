##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Test 'xmlrpc' ZCML Namespace directives.
"""

import unittest

from zope.configuration import xmlconfig
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.security.proxy import ProxyFactory
from zope.testing.cleanup import CleanUp as PlacelessSetup

from zope import component
from zope.app.publisher import xmlrpc


class IV(Interface):
    def index():
        "A method"


class IC(Interface):
    pass


@implementer(IV)
class V1:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def index(self):
        return 'V1 here'

    def action(self):
        return 'done'


class Request:

    def __init__(self, type):
        directlyProvides(self, type)


request = Request(IXMLRPCRequest)


@implementer(IC)
class Ob:
    pass


ob = Ob()


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def testView(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='test'), None)
        xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        view = component.queryMultiAdapter((ob, request), name='test')
        self.assertIn(V1, view.__class__.__bases__)
        self.assertIn(xmlrpc.MethodPublisher, view.__class__.__bases__)

    def testInterfaceProtectedView(self):
        xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = component.getMultiAdapter((ob, request), name='test2')
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = component.getMultiAdapter((ob, request), name='test3')
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = component.getMultiAdapter((ob, request), name='test4')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = component.getMultiAdapter((ob, request), name='test5')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedView(self):
        self.assertRaises(ConfigurationError, xmlconfig.file,
                          "xmlrpc_error.zcml", xmlrpc.tests)

    def testNoPermission(self):
        xmlconfig.file("xmlrpc_noperm.zcml", xmlrpc.tests)
        v = component.getMultiAdapter((ob, request), name='index')
        self.assertEqual(v.index(), 'V1 here')

    def test_no_name_no_permission(self):
        self.assertRaises(ConfigurationError, xmlconfig.file,
                          "xmlrpc_nonamenoperm.zcml", xmlrpc.tests)

    def test_no_name(self):
        xmlconfig.file("xmlrpc.zcml", xmlrpc.tests)
        v = component.getMultiAdapter((ob, request), name='index')
        self.assertEqual(v(), 'V1 here')
        v = component.getMultiAdapter((ob, request), name='action')
        self.assertEqual(v(), 'done')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
