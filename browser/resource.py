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
"""

$Id: resource.py,v 1.5 2003/08/16 00:43:46 srichter Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.component import queryView
from zope.context import getWrapperContainer, getInnerWrapperData
from zope.context import ContextMethod
from zope.app.traversing import joinPath
from zope.component.interfaces import IResourceService

class Resource:

    def __init__(self, request):
        self.request = request

    def __call__(wrapped_self):
        name = getInnerWrapperData(wrapped_self)['name']
        if name.startswith('++resource++'):
            name = name[12:]

        service = getWrapperContainer(wrapped_self)
        while not IResourceService.isImplementedBy(service):
            name = "%s/%s" % (getInnerWrapperData(service)['name'],
                              name)
            service = getWrapperContainer(service)

        site = getWrapperContainer(service)

        skin = wrapped_self.request.getPresentationSkin()
        if skin:
            skin = "++skin++%s" % skin

        base_url = wrapped_self.request.getApplicationURL(path_only=True)

        if site is not None:
            raise NotImplementedError("This code path is not tested")
            absolute_url = queryView(service,
                                     'absolute_url',
                                     wrapped_self.request)
            if absolute_url is not None:
                base_url = absolute_url()

        if skin:
            return joinPath(base_url, skin, '@@', name) # XXX joinPath should
        else:                                           # XXX eat empty path
            return joinPath(base_url, '@@', name)       # XXX elements

    __call__ = ContextMethod(__call__)
