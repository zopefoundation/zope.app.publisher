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
"""Global Browser Menu Tests

$Id$
"""
import unittest
from zope.exceptions import DuplicationError
from zope.security.interfaces import Forbidden, Unauthorized
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.security.management import newInteraction, endInteraction

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission
from zope.app.publisher.browser.globalbrowsermenuservice import \
     GlobalBrowserMenuService
from zope.app.tests.placelesssetup import PlacelessSetup

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


def d(n):
    return {'action': "a%s" % n,
            'title':  "t%s" % n,
            'description':  "d%s" % n,
            'selected': '',
            'extra': None
            }


class ParticipationStub(object):

    def __init__(self, principal):
        self.principal = principal
        self.interaction = None


class GlobalBrowserMenuServiceTest(PlacelessSetup, unittest.TestCase):

    def __reg(self):
        return GlobalBrowserMenuService()

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

        menu = r.getMenu('test_id', TestObject(), TestRequest())
        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])

    def test_w_class(self):
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
        r.menuItem('test_id', TestObject, 'a0', 't0', 'd0')

        menu = r.getMenu('test_id', TestObject(), TestRequest())
        self.assertEqual(list(menu), [d(0), d(5), d(6), d(3), d(2), d(1)])

    def test_w_class_that_does_not_implement(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')

        class C:
            pass

        # We provide a permission so C doesn't have to implement
        # IBrowserPublisher.  We use CheckerPublic so we don't have to set
        # up any other security machinery.

        from zope.security.checker import CheckerPublic
        r.menuItem('test_id', C, 'a0', 't0', 'd0', permission=CheckerPublic)
        r.menuItem('test_id', C, 'a10', 't10', 'd10', permission=CheckerPublic)

        menu = r.getMenu('test_id', C(), TestRequest())
        self.assertEqual(list(menu), [d(0), d(10)])

    def test_w_permission(self):
        ztapi.provideUtility(IPermission, Permission('p', 'P'), 'p')

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

        endInteraction()
        newInteraction(ParticipationStub('test'))

        menu = r.getMenu('test_id', TestObject(), TestRequest())

        self.assertEqual(list(menu), [d(6), d(3), d(2), d(1)])

        endInteraction()
        newInteraction()
        menu = r.getMenu('test_id', TestObject(), TestRequest())
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

        menu = r.getMenu('test_id', TestObject(), TestRequest())
        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])

    def test_identify_action(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', Interface, 'a1', 't1', 'd1')
        r.menuItem('test_id', I11, 'a12', 't12', 'd12')
        r.menuItem('test_id', I111, 'a2', 't2', 'd2')

        def d(n, selected=''):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "d%s" % n,
                    'selected': selected,
                    'extra': None}

        menu = r.getMenu('test_id', TestObject(),
            TestRequest(SERVER_URL='http://127.0.0.1/a1', PATH_INFO='/a1'))
        self.assertEqual(list(menu), [d(2), d(12), d(1, 'selected')])
        menu = r.getMenu('test_id', TestObject(), 
            TestRequest(SERVER_URL='http://127.0.0.1/a12', PATH_INFO='/a12'))
        self.assertEqual(list(menu), [d(2), d(12, 'selected'), d(1)])
        menu = r.getMenu('test_id', TestObject(),
            TestRequest(SERVER_URL='http://127.0.0.1/@@a1', PATH_INFO='/@@a1'))
        self.assertEqual(list(menu), [d(2), d(12), d(1, 'selected')])
        menu = r.getMenu('test_id', TestObject(), 
            TestRequest(SERVER_URL='http://127.0.0.1/@@a12',
            PATH_INFO='/@@a12'))
        self.assertEqual(list(menu), [d(2), d(12, 'selected'), d(1)])
        menu = r.getMenu('test_id', TestObject(),
            TestRequest(SERVER_URL='http://127.0.0.1/++view++a1',
            PATH_INFO='/++view++a1'))
        self.assertEqual(list(menu), [d(2), d(12), d(1, 'selected')])
        menu = r.getMenu('test_id', TestObject(), 
            TestRequest(SERVER_URL='http://127.0.0.1/++view++a12',
            PATH_INFO='/++view++a12'))
        self.assertEqual(list(menu), [d(2), d(12, 'selected'), d(1)])


    def test_identify_similar_action(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', I11, 'aA', 'tA', 'dA')
        r.menuItem('test_id', I111, 'aAaA', 'tAaA', 'dAaA')

        def d(s, selected=''):
            return {'action': "a%s" % s,
                    'title':  "t%s" % s,
                    'description':  "d%s" % s,
                    'selected': selected,
                    'extra': None}

        menu = r.getMenu('test_id', TestObject(),
            TestRequest(SERVER_URL='http://127.0.0.1/aA', PATH_INFO='/aA'))
        self.assertEqual(list(menu), [d('AaA'), d('A', 'selected')])
        menu = r.getMenu('test_id', TestObject(), 
            TestRequest(SERVER_URL='http://127.0.0.1/aAaA', PATH_INFO='/aAaA'))
        self.assertEqual(list(menu), [d('AaA', 'selected'), d('A')])


    def testEmpty(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        menu = r.getMenu('test_id', TestObject(), TestRequest())
        self.assertEqual(list(menu), [])

    def test_getAllMenuItema(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', Interface, 'a1', 't1', 'd1')
        r.menuItem('test_id', I1, 'a2', 't2', 'd2')
        r.menuItem('test_id', I11, 'a3', 't3', 'd3')
        r.menuItem('test_id', I111, 'a5', 't5', 'd5')
        r.menuItem('test_id', I111, 'a6', 't6', 'd6')
        r.menuItem('test_id', I111, 'a7', 't7', 'd7')
        r.menuItem('test_id', I111, 'a8', 't8', 'd8')
        r.menuItem('test_id', I12, 'a9', 't9', 'd9')

        def d(n):
            return ('a%s' %n, 't%s' %n, 'd%s' %n, None, None, None) 

        menu = [(item.action, item.title, item.description,
                 item.filter, item.permission, item.extra)
                for item in r.getAllMenuItems('test_id', TestObject())
                ]
        self.assertEqual(menu, [d(5), d(6), d(7), d(8), d(3), d(2), d(1)])

    def test_addWrong(self):
        r = self.__reg()
        
        x = []
        r.menu('test_id', 'test menu')
        self.assertRaises(TypeError, r.menuItem, 'test_id', x, 'a1', 'a2',' a3')

    def test_addClass(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', C1, 'a1', 'a2', 'a3')

def test_suite():
    return unittest.makeSuite(GlobalBrowserMenuServiceTest)

if __name__ == '__main__':
    unittest.main()
