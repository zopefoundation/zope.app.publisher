##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_globalbrowsermenuservice.py,v 1.6 2003/02/11 15:59:54 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.exceptions import Forbidden, Unauthorized, DuplicationError
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.app.tests.placelesssetup import PlacelessSetup

from zope.component.service import serviceManager
from zope.component.servicenames import Permissions
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.app.interfaces.security import IPermissionService
from zope.security.management import newSecurityManager
from zope.security.management import noSecurityManager, system_user

class I1(Interface): pass
class I11(I1): pass
class I12(I1): pass
class I111(I11): pass

class X:
    __implements__ = IBrowserPublisher, I111

    def f(self): pass

    def browserDefault(self, r): return self, ()
    def publishTraverse(self, request, name):
        if name[:1] == 'f':
            raise Forbidden, name
        if name[:1] == 'u':
            raise Unauthorized, name
        return self.f


class Test(PlacelessSetup, TestCase):

    def __reg(self):
        from zope.app.publisher.browser.globalbrowsermenuservice \
             import GlobalBrowserMenuService

        r = GlobalBrowserMenuService()
        return r

    def testDup(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        self.assertRaises(DuplicationError, r.menu, 'test_id', 'test menu')

    def test(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', Interface, 'a1', 't1', 'd1')
        r.menuItem('test_id', I1, 'a2', 't2', 'd2')
        r.menuItem('test_id', I11, 'a3', 't3', 'd3', 'context')
        r.menuItem('test_id', I11, 'a4', 't4', 'd4', 'not:context')
        r.menuItem('test_id', I111, 'a5', 't5', 'd5')
        r.menuItem('test_id', I111, 'a6', 't6', 'd6')
        r.menuItem('test_id', I111, 'f7', 't7', 'd7')
        r.menuItem('test_id', I111, 'u8', 't8', 'd8')
        r.menuItem('test_id', I12, 'a9', 't9', 'd9')

        menu = r.getMenu('test_id', X(), TestRequest())

        def d(n):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "d%s" % n,
                    'selected': ''
                    }

        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])

    def test_w_permission(self):
        serviceManager.defineService(Permissions, IPermissionService)
        serviceManager.provideService(Permissions, permissionRegistry)
        permissionRegistry.definePermission('p', 'P')
        
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', Interface, 'a1', 't1', 'd1')
        r.menuItem('test_id', I1, 'a2', 't2', 'd2')
        r.menuItem('test_id', I11, 'a3', 't3', 'd3', 'context')
        r.menuItem('test_id', I11, 'a4', 't4', 'd4', 'not:context')
        r.menuItem('test_id', I111, 'a5', 't5', 'd5', permission='p')
        r.menuItem('test_id', I111, 'a6', 't6', 'd6')
        r.menuItem('test_id', I111, 'f7', 't7', 'd7')
        r.menuItem('test_id', I111, 'u8', 't8', 'd8')
        r.menuItem('test_id', I12, 'a9', 't9', 'd9')

        def d(n):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "d%s" % n,
                    'selected': ''
                    }

        newSecurityManager('test')

        menu = r.getMenu('test_id', X(), TestRequest())

        self.assertEqual(list(menu), [d(6), d(3), d(2), d(1)])

        newSecurityManager(system_user)

        menu = r.getMenu('test_id', X(), TestRequest())

        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])
        

    def test_no_dups(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', Interface, 'a1', 't1', 'd1')
        r.menuItem('test_id', Interface, 'a12', 't2', 'd12')
        r.menuItem('test_id', I1, 'a2', 't2', 'd2')
        r.menuItem('test_id', I1, 'a23', 't3', 'd23')
        r.menuItem('test_id', I1, 'a24', 't4', 'd24')
        r.menuItem('test_id', I11, 'a3', 't3', 'd3', 'context')
        r.menuItem('test_id', I11, 'a4', 't4', 'd4', 'not:context')
        r.menuItem('test_id', I111, 'a5', 't5', 'd5')
        r.menuItem('test_id', I111, 'a6', 't6', 'd6')
        r.menuItem('test_id', I111, 'f7', 't7', 'd7')
        r.menuItem('test_id', I111, 'u8', 't8', 'd8')
        r.menuItem('test_id', I12, 'a9', 't9', 'd9')

        menu = r.getMenu('test_id', X(), TestRequest())

        def d(n):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "d%s" % n,
                    'selected': ''}

        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])

    def testEmpty(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        menu = r.getMenu('test_id', X(), TestRequest())
        self.assertEqual(list(menu), [])


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
