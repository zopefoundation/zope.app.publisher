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
"""

$Id: test_directives.py,v 1.3 2002/12/31 03:35:10 jim Exp $
"""

import unittest

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.component.tests.views import IC, V1, VZMI, R1, RZMI
from zope.component import getView, queryView
from zope.component import getDefaultViewName
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.proxy import ProxyFactory
from cStringIO import StringIO

from zope.component.tests.request import Request

from zope.publisher.interfaces.xmlrpc import IXMLRPCPresentation

import zope.app.publisher.xmlrpc

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:xmlrpc='http://namespaces.zope.org/xmlrpc'>
   %s
   </zopeConfigure>"""

request = Request(IXMLRPCPresentation)

class Ob:
    __implements__ = IC

ob = Ob()

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', zope.app.publisher.xmlrpc)()

    def testView(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template % (
            """
            <xmlrpc:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC" />
            """
            )))

        self.assertEqual(
            queryView(ob, 'test', request).__class__,
            V1)


    def testInterfaceProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')


    def testAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  allowed_methods="action"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')


    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  allowed_methods="action"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')


    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  allowed_methods="action index"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')


    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  allowed_methods="action index"
                  />
            """
            ))


    def testMethodViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <xmlrpc:view
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC">

                <xmlrpc:method name="index.html" attribute="index" />
                <xmlrpc:method name="action.html" attribute="action" />
            </xmlrpc:view>
            """
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')


    def testMethodViewsWithName(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC">

                <xmlrpc:method name="index.html" attribute="index" />
                <xmlrpc:method name="action.html" attribute="action" />
            </xmlrpc:view>
            """
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')
        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')


    def testProtectedMethodViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
               zope.app.security.registries.metaconfigure.definePermission" />
            </directives>

            <permission id="XXX" title="xxx" />

            <xmlrpc:view
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="XXX">

                <xmlrpc:method name="index.html" attribute="index" />
                <xmlrpc:method name="action.html" attribute="action"
                              permission="zope.Public" />
            </xmlrpc:view>
            """
            ))

        # Need to "log someone in" to turn on checks
        from zope.security.management import newSecurityManager
        newSecurityManager('someuser')

        v = getView(ob, 'index.html', request)
        self.assertRaises(Exception, v)
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
