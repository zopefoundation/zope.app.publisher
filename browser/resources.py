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
"""Resource URL acess

$Id$
"""
from zope.app.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.exceptions import NotFoundError
from zope.interface import implements

from zope.app import zapi
from zope.app.location import locate
from zope.app.servicenames import Presentation

class Resources(BrowserView):
    """Provide a URL-accessible resource namespace
    """

    implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''

        resource_service = zapi.getService(Presentation)
        resource = resource_service.queryResource(name, request)
        if resource is None:
            raise NotFoundError(self, name)

        locate(resource, resource_service, name)
        return resource

    def browserDefault(self, request):
        '''See IBrowserPublisher'''
        return empty, ()

    def __getitem__(self, name):
        return self.publishTraverse(self.request, name)


def empty():
    return ''
