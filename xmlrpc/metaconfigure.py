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
"""XMLRPC configuration code

$Id: metaconfigure.py,v 1.18 2004/03/15 20:42:19 jim Exp $
"""

from zope.component.servicenames import Presentation
from zope.app.component.metaconfigure import handler
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.security.checker import CheckerPublic, Checker
from zope.app.component.interface import provideInterface


def view(_context, name, class_=None, for_=None, layer=None,
         permission=None, allowed_interface=None, allowed_attributes=None):

    if layer is not None:
        raise ConfigurationError("Layers are not supported for XML-RPC.")
    
    if name is None:
        raise ConfigurationError("You must specify a view name.") 
    
    if ((allowed_attributes or allowed_interface)
        and ((name is None) or not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )
    
    allowed_interface = allowed_interface or []
    allowed_attributes = allowed_attributes or []

    # If there were special permission settings provided, then use them
    if permission:
        if permission == 'zope.Public':
            permission = CheckerPublic
    
        require = {}
        for attr_name in allowed_attributes:
            require[attr_name] = permission
    
        if allowed_interface:
            for iface in allowed_interface:
                for field_name in iface:
                    require[field_name] = permission
    
        checker = Checker(require.get)
    
        def proxyView(context, request, class_=class_, checker=checker):
            view = class_(context, request)
            # We need this in case the resource gets unwrapped and
            # needs to be rewrapped
            view.__Security_checker__ = checker
            return view
    
        class_ =  proxyView

    # Register the new view.
    _context.action(
        discriminator = ('view', tuple(for_), name, IXMLRPCRequest),
        callable = handler,
        args = (Presentation, 'provideAdapter', IXMLRPCRequest, class_,
                name, for_) )

    # Register the used interfaces with the interface service
    for iface in for_:
        if iface is not None:
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', iface)
                )
        

def defaultView(_context, name, for_=None):
    """Declare the view having the passed name as the default view."""
    _context.action(
        discriminator = ('defaultViewName', for_, IXMLRPCRequest, name),
        callable = handler,
        args = (Presentation, 'setDefaultViewName', for_, IXMLRPCRequest, name)
        )
