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

$Id: resource.py,v 1.2 2002/12/25 14:13:09 jim Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.component import queryView
from zope.proxy.context import getWrapperContainer, getInnerWrapperData
from zope.proxy.context import ContextMethod

class Resource:

    def __init__(self, request):
        self.request = request

    def __call__(wrapped_self):
        name = getInnerWrapperData(wrapped_self)['name']
        if name.startswith('++resource++'):
            name = name[12:]

        service = getWrapperContainer(wrapped_self)
        site = getWrapperContainer(service)

        skin = wrapped_self.request.getPresentationSkin()
        if skin:
            skin = "++skin++%s/" % skin

        if site is None:
            return "/%s@@/%s" % (skin, name)

        absolute_url = queryView(service,
                                 'absolute_url',
                                 wrapped_self.request)

        if absolute_url is None:
            return "/%s@@/%s" % (skin, name)

        site_url = absolute_url()

        return "%s/%s@@/%s" % (site_url, skin, name)

    __call__ = ContextMethod(__call__)
