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

Revision information:
$Id: test_resources.py,v 1.3 2002/12/31 02:52:03 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.resource import provideResource
from zope.component.adapter import provideAdapter

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserView

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)


    def test(self):
        from zope.app.publisher.browser.resources import Resources
        request = TestRequest()

        class Resource:
            def __init__(self, request): pass
            def __call__(self): return 42

        provideResource('test', IBrowserView, Resource)
        view = Resources(None, request)
        resource = view.publishTraverse(request, 'test')
        self.assertEqual(resource(), 42)

    def testNotFound(self):
        from zope.app.publisher.browser.resources import Resources
        from zope.exceptions import NotFoundError
        request = TestRequest()
        view = Resources(None, request)
        self.assertRaises(NotFoundError,
                          view.publishTraverse,
                          request, 'test'
                          )



def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
