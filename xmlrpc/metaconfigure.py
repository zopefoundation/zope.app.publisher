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

$Id: metaconfigure.py,v 1.12 2003/08/03 23:47:47 srichter Exp $
"""
from zope.app.component.metaconfigure import handler
from zope.app.services.servicenames import Interfaces
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.xmlrpc import IXMLRPCPresentation
from zope.security.proxy import Proxy
from zope.security.checker import CheckerPublic, NamesChecker, Checker


class view(object):
    '''This view class handles the directives for the XML-RPC Presentation'''

    type = IXMLRPCPresentation

    def __init__(self, _context, name=None, factory=None, for_=None,
                 permission=None, allowed_interface=None,
                 allowed_methods=None):

        self.for_ = for_

        if ((allowed_methods or allowed_interface)
            and ((name is None) or not permission)):
            raise ConfigurationError(
                "Must use name attribute with allowed_interface or "
                "allowed_methods"
                )

        self._context = _context
        self.factory = factory
        self.name = name
        self.permission = permission
        self.allowed_methods = allowed_methods
        self.allowed_interface = allowed_interface
        self.methods = 0


    def method(self, _context, name, attribute, permission=None):
        permission = permission or self.permission
        # make a copy of the factory sequence, since we might modify it
        # specifically for this method.
        factory = self.factory[:]

        # if a specific permission was specified for this method we have to
        # apply a new proxy.
        if permission:
            if permission == 'zope.Public':
                permission = CheckerPublic

            def methodView(context, request, factory=factory[-1],
                           attribute=attribute, permission=permission):

                return Proxy(getattr(factory(context, request), attribute),
                             NamesChecker(__call__ = permission))
        else:

            def methodView(context, request, factory=factory[-1],
                           attribute=attribute):
                return getattr(factory(context, request), attribute)

        factory[-1] = methodView

        self.methods += 1

        _context.action(
            discriminator = ('view', self.for_, name, self.type),
            callable = handler,
            args = ('Views', 'provideView', self.for_, name, self.type, factory)
            )


    def _proxyFactory(self, factory, checker):
        factory = factory[:]

        def proxyView(context, request, factory=factory[-1], checker=checker):

            view = factory(context, request)

            # We need this in case the resource gets unwrapped and
            # needs to be rewrapped
            view.__Security_checker__ = checker

            return view

        factory[-1] =  proxyView

        return factory


    def __call__(self):
        if self.name is None:
            return

        permission = self.permission
        allowed_interface = self.allowed_interface or []
        allowed_methods = self.allowed_methods or []
        factory = self.factory[:]


        if permission:
            if permission == 'zope.Public':
                permission = CheckerPublic

            require = {}
            for name in allowed_methods:
                require[name] = permission

            if allowed_interface:
                for iface in allowed_interface:
                    for name in iface:
                        require[name] = permission

            checker = Checker(require.get)

            def proxyView(context, request,
                          factory=factory[-1], checker=checker):
                view = factory(context, request)
                # We need this in case the resource gets unwrapped and
                # needs to be rewrapped
                view.__Security_checker__ = checker
                return view

            factory[-1] =  proxyView

        self._context.action(
            discriminator = ('view', self.for_, self.name, self.type),
            callable = handler,
            args = ('Views', 'provideView', self.for_, self.name,
                    self.type, factory) )

        if self.for_ is not None:
            self._context.action(
                discriminator = None,
                callable = handler,
                args = (Interfaces, 'provideInterface',
                        self.for_.__module__+'.'+self.for_.__name__, self.for_)
                )
