##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Support for tests that need a simple site to be provided.

$Id$
"""
import zope.component
from zope.interface import implements
from zope.traversing.interfaces import IContainmentRoot

from zope.app.component.hooks import setSite
from zope.app.component.interfaces import ISite

from zope.app.publisher.browser.menu import BrowserMenu

class Site:
    implements(ISite, IContainmentRoot)

    def getSiteManager(self):
        return zope.component.getGlobalSiteManager()

site = Site()


class SiteHandler(object):

    def setUp(self):
        super(SiteHandler, self).setUp()
        setSite(site)

    def tearDown(self):
        setSite()
        super(SiteHandler, self).tearDown()

class M1(BrowserMenu):
    pass

