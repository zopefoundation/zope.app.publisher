##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Browser Menu Browser Tests

$Id$
"""
import unittest

from zope.interface import Interface, implements
from zope.component import getGlobalServices

from zope.security.management import newInteraction
from zope.security.checker import defineChecker, NamesChecker, CheckerPublic
from zope.security.proxy import ProxyFactory

from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.publisher.interfaces.browser import IBrowserView

from zope.app.tests import ztapi
from zope.app.servicenames import BrowserMenu
from zope.app.site.tests.placefulsetup import PlacefulSetup

from zope.app.publisher.interfaces.browser import IBrowserMenuService
from zope.app.publisher.browser.globalbrowsermenuservice import MenuAccessView
from zope.app.publication.traversers import TestTraverser
from zope.app.site.interfaces import ISimpleService

def d(title, action):
    return {'action': action, 'title': title, 'description': ''}

class Service(object):
    implements(IBrowserMenuService, ISimpleService)

    def getMenu(self, name, ob, req):
        return [d('l1', 'a1'),
                d('l2', 'a2/a3'),
                d('l3', '@@a3'),]

class I(Interface): pass
class C(object):
    implements(I)

    def __call__(self):
        pass

ob = C()
ob.a1 = C()
ob.a2 = C()
ob.a2.a3 = C()
ob.abad = C()
ob.abad.bad = 1

class V(object):
    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        pass

class ParticipationStub(object):

    def __init__(self, principal):
        self.principal = principal
        self.interaction = None


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        defineService = getGlobalServices().defineService
        provideService = getGlobalServices().provideService

        defineService(BrowserMenu, IBrowserMenuService)
        provideService(BrowserMenu, Service())
        ztapi.browserView(I, 'a3', V)
        ztapi.browserViewProviding(None, IBrowserPublisher, TestTraverser)
        defineChecker(C, NamesChecker(['a1', 'a2', 'a3', '__call__'],
                                      CheckerPublic,
                                      abad='waaa'))

    def test(self):
        from zope.security.management import endInteraction
        endInteraction()
        newInteraction(ParticipationStub('who'))
        v = MenuAccessView(ProxyFactory(ob), TestRequest())
        self.assertEqual(v['zmi_views'],
                         [{'description': '', 'title':'l1', 'action':'a1'},
                          {'description': '', 'title':'l2', 'action':'a2/a3'},
                          {'description': '', 'title':'l3', 'action':'@@a3'}
                          ])


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
