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
"""Resource URL acess

$Id: resources.py,v 1.9 2003/06/07 05:46:02 stevea Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.component import getService
from zope.app.services.servicenames import Resources as ResourceService
from zope.app.context import ContextWrapper
from zope.context import ContextMethod
from zope.exceptions import NotFoundError
from zope.interface import implements

class Resources(BrowserView):
    """Provide a URL-accessible resource namespace
    """

    implements(IBrowserPublisher)

    def publishTraverse(wrapped_self, request, name):
        '''See interface IBrowserPublisher'''

        resource_service = getService(wrapped_self, ResourceService)
        resource = resource_service.queryResource(wrapped_self, name, request)
        if resource is None:
            raise NotFoundError(wrapped_self, name)
        return ContextWrapper(resource, resource_service, name=name)

    publishTraverse = ContextMethod(publishTraverse)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return empty, ()

    def __getitem__(self, name):
        return self.publishTraverse(self.request, name)

    __getitem__ = ContextMethod(__getitem__)

def empty():
    return ''
