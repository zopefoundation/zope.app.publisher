##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Provide zope app-server customizatioin of publisher browser facilities

$Id$
"""
from zope.interface import implements, directlyProvidedBy, directlyProvides
from zope.app.location import Location
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import ISkin

class BrowserView(Location):
    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context


def applySkin(request, skin):
    """Change the presentation skin for this request.

    >>> import pprint
    >>> from zope.interface import Interface, providedBy
    >>> class SkinA(Interface): pass
    >>> directlyProvides(SkinA, ISkin)
    >>> class SkinB(Interface): pass
    >>> directlyProvides(SkinB, ISkin)
    >>> class IRequest(Interface): pass
    
    >>> class Request(object):
    ...     implements(IRequest)
    
    >>> req = Request()

    >>> applySkin(req, SkinA)
    >>> pprint.pprint(list(providedBy(req).interfaces()))
    [<InterfaceClass zope.app.publisher.browser.SkinA>,
     <InterfaceClass zope.app.publisher.browser.IRequest>]

    >>> applySkin(req, SkinB)
    >>> pprint.pprint(list(providedBy(req).interfaces()))
    [<InterfaceClass zope.app.publisher.browser.SkinB>,
     <InterfaceClass zope.app.publisher.browser.IRequest>]
    """
    old_skins = [iface for iface in directlyProvidedBy(request)
                 if ISkin.providedBy(iface)]

    for old_skin in old_skins:
        directlyProvides(request, directlyProvidedBy(request) - old_skin)

    directlyProvides(request, skin)
