##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Browser Menu Directives Tests

$Id$
"""
import unittest

from zope.configuration.xmlconfig import XMLConfig
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.security.interfaces import Unauthorized, Forbidden

from zope.app.testing.placelesssetup import PlacelessSetup

import zope.app.publisher.browser

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""

class I1(Interface): pass
class I11(I1): pass
class I12(I1): pass
class I111(I11): pass

class C1(object):
    implements(I1)
            
class TestObject(object):
    implements(IBrowserPublisher, I111)

    def f(self):
        pass

    def browserDefault(self, r):
        return self, ()

    def publishTraverse(self, request, name):
        if name[:1] == 'f':
            raise Forbidden, name
        if name[:1] == 'u':
            raise Unauthorized, name
        return self.f


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.publisher.browser)()

    def test(self):
        XMLConfig('tests/menus.zcml', zope.app.publisher.browser)()

        from zope.app.menus import test_id
        
        menu = zope.app.publisher.browser.menu.getMenu(
            test_id, TestObject(), TestRequest())

        def d(n):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "",
                    'selected': '',
                    'icon': None,
                    'extra': None}

        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])

        first = zope.app.publisher.browser.menu.getFirstMenuItem(
            test_id, TestObject(), TestRequest())

        self.assertEqual(first, d(5))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
