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
"""Selecting first available and allowed management view

$Id$
"""
from zope.interface import implements
from zope.app.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app import zapi
from zope.app.servicenames import BrowserMenu

class ManagementViewSelector(BrowserView):
    """View that selects the first available management view."""
    implements(IBrowserPublisher)

    def browserDefault(self, request):
        return self, ()

    def __call__(self):
        browser_menu_service = zapi.getService(BrowserMenu)
        item = browser_menu_service.getFirstMenuItem(
            'zmi_views', self.context, self.request)

        if item:
            self.request.response.redirect(item['action'])
            return u''

        self.request.response.redirect('.') # Redirect to content/
        return u''
