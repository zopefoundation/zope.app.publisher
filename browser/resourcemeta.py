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
"""Browser configuration code

$Id: resourcemeta.py,v 1.2 2002/12/25 14:13:09 jim Exp $
"""

from zope.security.proxy import Proxy
from zope.security.checker \
     import CheckerPublic, NamesChecker, Checker

from zope.interfaces.configuration import INonEmptyDirective
from zope.interfaces.configuration import ISubdirectiveHandler
from zope.configuration.action import Action
from zope.configuration.exceptions import ConfigurationError

from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.app.component.metaconfigure import handler

from zope.app.publisher.browser.fileresource \
     import FileResourceFactory, ImageResourceFactory

class resource(object):

    __class_implements__ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    type = IBrowserPresentation
    default_allowed_attributes = '__call__'  # space separated string

    def __init__(self, _context, factory=None, name=None, layer='default',
                 permission=None,
                 allowed_interface=None, allowed_attributes=None,
                 file=None, image=None):

        if ((allowed_attributes or allowed_interface)
            and ((name is None) or not permission)):
            raise ConfigurationError(
                "Must use name attribute with allowed_interface or "
                "allowed_attributes"
                )

        if allowed_interface is not None:
            allowed_interface = _context.resolve(allowed_interface)

        self.__file = file
        self.__image = image

        self.factory = self._factory(_context, factory)
        self.layer = layer
        self.name = name
        self.permission = permission
        self.allowed_attributes = allowed_attributes
        self.allowed_interface = allowed_interface
        self.pages = 0

    def _factory(self, _context, factory):
        if ((factory is not None)
            + (self.__file is not None)
            + (self.__image is not None)
            ) > 1:
            raise ConfigurationError(
                "Can't use more than one of factory, file, and image "
                "attributes for resource directives"
                )

        if factory is not None:
            return _context.resolve(factory)

        if self.__file is not None:
            return FileResourceFactory(_context.path(self.__file))

        if self.__image is not None:
            return ImageResourceFactory(_context.path(self.__image))

        raise ConfigurationError(
            "At least one of the factory, file, and image "
            "attributes for resource directives must be specified"
            )


    def page(self, _context, name, attribute, permission=None,
             layer=None, factory=None):

        permission = permission or self.permission

        factory = self._pageFactory(factory or self.factory,
                                    attribute, permission)

        self.pages += 1

        if layer is None:
            layer = self.layer

        return [
            Action(
                discriminator = self._discriminator(name, layer),
                callable = handler,
                args = self._args(name, factory, layer),
                )
            ]

    def _discriminator(self, name, layer):
        return ('resource', name, self.type, layer)

    def _args(self, name, factory, layer):
        return ('Resources', 'provideResource',
                name, self.type, factory, layer)

    def _pageFactory(self, factory, attribute, permission):
        if permission:
            if permission == 'zope.Public':
                permission = CheckerPublic

            def pageView(request,
                         factory=factory, attribute=attribute,
                         permission=permission):
                return Proxy(getattr(factory(request), attribute),
                             NamesChecker(__call__ = permission))

        else:

            def pageView(request,
                         factory=factory, attribute=attribute):
                return getattr(factory(request), attribute)

        return pageView

    def __call__(self, require=None):
        if self.name is None:
            return ()

        permission = self.permission
        allowed_interface = self.allowed_interface
        allowed_attributes = self.allowed_attributes
        factory = self.factory

        if permission:
            if require is None:
                require = {}

            if permission == 'zope.Public':
                permission = CheckerPublic

            if ((not allowed_attributes) and (allowed_interface is None)
                and (not self.pages)):
                allowed_attributes = self.default_allowed_attributes

            for name in (allowed_attributes or '').split():
                require[name] = permission

            if allowed_interface:
                for name in allowed_interface.names(1):
                    require[name] = permission

        if require:
            checker = Checker(require.get)

            factory = self._proxyFactory(factory, checker)


        return [
            Action(
                discriminator = self._discriminator(self.name, self.layer),
                callable = handler,
                args = self._args(self.name, factory, self.layer),
                )
            ]

    def _proxyFactory(self, factory, checker):
        def proxyView(request,
                      factory=factory, checker=checker):
            resource = factory(request)

            # We need this in case the resource gets unwrapped and
            # needs to be rewrapped
            resource.__Security_checker__ = checker

            return Proxy(resource, checker)

        return proxyView
