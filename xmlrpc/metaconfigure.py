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
"""XMLRPC configuration code

$Id$
"""

from zope.component.servicenames import Presentation
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.metaconfigure import handler
import zope.interface

from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.security.checker import CheckerPublic, Checker
from zope.app.component.interface import provideInterface

import zope.app.location

def view(_context, for_=None, interface=None, methods=None,
         class_=None,  permission=None, name=None):
    
    interface = interface or []
    methods = methods or []

    # If there were special permission settings provided, then use them
    if permission == 'zope.Public':
        permission = CheckerPublic

    require = {}
    for attr_name in methods:
        require[attr_name] = permission

    if interface:
        for iface in interface:
            for field_name in iface:
                require[field_name] = permission
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', for_)
                )

    if name:
        # Register a single view
        
        if permission:
            checker = Checker(require)

            def proxyView(context, request, class_=class_, checker=checker):
                view = class_(context, request)
                # We need this in case the resource gets unwrapped and
                # needs to be rewrapped
                view.__Security_checker__ = checker
                return view

            class_ =  proxyView

        # Register the new view.
        _context.action(
            discriminator = ('view', for_, name, IXMLRPCRequest),
            callable = handler,
            args = (Presentation, 'provideAdapter', IXMLRPCRequest, class_,
                    name, (for_, )) )
    else:
        if permission:
            checker = Checker({'__call__': permission})
        else:
            checker = None
            
        for name in require:
            _context.action(
                discriminator = ('view', for_, name, IXMLRPCRequest),
                callable = handler,
                args = (Presentation, 'provideAdapter', IXMLRPCRequest,
                        MethodFactory(class_, name, checker),
                        name, (for_, )) )

    # Register the used interfaces with the interface service
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )
        


class MethodFactory:

    def __init__(self, cls, name, checker):
        self.cls, self.name, self.checker = cls, name, checker

    def __call__(self, context, request):
        ob = self.cls(context, request)
        ob = getattr(ob, self.name)
        if self.checker is not None:
            ob = ProtectedMethod(ob, self.checker)
        return ob


class ProtectedMethod:

    zope.interface.implements(zope.app.location.ILocation)

    __parent__ = __name__ = None

    def __init__(self, ob, checker):
        self.ob = ob
        self.__Security_checker__ = checker

    def __call__(self, *args):
        return self.ob(*args)
    
