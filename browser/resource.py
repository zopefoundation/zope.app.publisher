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
"""Browser Resource

$Id$
"""
from zope.component.interfaces import IResource
from zope.interface import implements

from zope.app import zapi
from zope.app.component.hooks import getSite
from zope.app.location import Location
from zope.app.traversing.browser.interfaces import IAbsoluteURL


class Resource(Location):
    implements(IResource)

    def __init__(self, request):
        self.request = request

    def __call__(self):
        name = self.__name__
        if name.startswith('++resource++'):
            name = name[12:]

        site = getSite()
        url = str(zapi.getViewProviding(site, IAbsoluteURL, self.request))
        return "%s/@@/%s" % (url, name)
