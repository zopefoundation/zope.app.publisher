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

$Id: viewmeta.py,v 1.3 2002/12/28 14:14:09 jim Exp $
"""

# XXX this will need to be refactored soon. :)

from zope.security.proxy import Proxy
from zope.security.checker import CheckerPublic, NamesChecker, Checker

from zope.interfaces.configuration import INonEmptyDirective
from zope.interfaces.configuration import ISubdirectiveHandler
from zope.configuration.action import Action
from zope.configuration.exceptions import ConfigurationError

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.component.metaconfigure import handler

from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.proxy.context import ContextMethod


class view:

    default_allowed_attributes = '__call__'  # space separated string

    __class_implements__ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    __pages = None
    __default = None

    def __init__(self, _context, factory=None, name=None, for_=None,
                 layer='default',
                 permission=None,
                 allowed_interface=None, allowed_attributes=None,
                 template=None, class_=None):

        if class_ and factory:
            raise ConfigurationError("Can't specify a class and a factory")

        factory = factory or class_

        if template:
            if name is None:
                raise ConfigurationError(
                    "Must specify name for template view")

            self.default_allowed_attributes = (
                '__call__ __getitem__ browserDefault')

            template = _context.path(template)

        self.template = template

        if for_ is not None:
            for_ = _context.resolve(for_)
        self.for_ = for_

        if ((allowed_attributes or allowed_interface)
            and ((name is None) or not permission)):
            raise ConfigurationError(
                "Must use name attribute with allowed_interface or "
                "allowed_attributes"
                )

        if allowed_interface is not None:
            allowed_interface = _context.resolve(allowed_interface)

        self.factory = self._factory(_context, factory)
        self.layer = layer
        self.name = name
        self.permission = permission
        self.allowed_attributes = allowed_attributes
        self.allowed_interface = allowed_interface
        self.pages = 0

        if name:
            self.__pages = {}


    def page(self, _context, name, attribute=None, permission=None,
             layer=None, template=None):

        if self.template:
            raise ConfigurationError(
                "Can't use page or defaultPage subdirectives for simple "
                "template views")

        self.pages += 1

        if self.name:
            # Named view with pages.

            if layer is not None:
                raise ConfigurationError(
                    "Can't specify a separate layer for pages of named "
                    "templates.")

            if template is not None:
                template = _context.path(template)

            self.__pages[name] = attribute, permission, template
            if self.__default is None:
                self.__default = name



            return ()

        factory = self.factory

        if template is not None:
            attribute = attribute or '__template__'
            klass = factory[-1]
            klass = type(klass.__name__, (klass, object), {
                attribute:
                ViewPageTemplateFile(_context.path(template))
                })
            factory = factory[:]
            factory[-1] = klass

        permission = permission or self.permission

        factory = self._pageFactory(factory or self.factory,
                                    attribute, permission)

        if layer is None:
            layer = self.layer

        return [
            Action(
                discriminator = ('view', self.for_, name,
                                 IBrowserPresentation, layer),
                callable = handler,
                args = ('Views', 'provideView',
                        self.for_, name, IBrowserPresentation, factory, layer),
                )
            ]


    def defaultPage(self, _context, name):
        if self.name:
            self.__default = name
            return ()

        return [Action(
            discriminator = ('defaultViewName', self.for_,
                             IBrowserPresentation, name),
            callable = handler,
            args = ('Views','setDefaultViewName', self.for_,
                    IBrowserPresentation, name),
            )]


    def _factory(self, _context, factory):
        if self.template:
            if factory:
                factory = map(_context.resolve, factory.strip().split())
                bases = (factory[-1], )
                klass = SimpleViewClass(
                    str(_context.path(self.template)),
                    used_for=self.for_, bases=bases
                    )
                factory[-1] = klass
                return factory

            return [SimpleViewClass(
                str(_context.path(self.template)),
                used_for = self.for_
                )]
        else:
            return map(_context.resolve, factory.strip().split())

    def _pageFactory(self, factory, attribute, permission):
        factory = factory[:]
        if permission:
            if permission == 'zope.Public':
                permission = CheckerPublic

            def pageView(context, request,
                         factory=factory[-1], attribute=attribute,
                         permission=permission):
                return Proxy(getattr(factory(context, request), attribute),
                             NamesChecker(__call__ = permission))
        else:
            def pageView(context, request,
                         factory=factory[-1], attribute=attribute):
                return getattr(factory(context, request), attribute)
        factory[-1] = pageView
        return factory

    def _proxyFactory(self, factory, checker):
        factory = factory[:]

        def proxyView(context, request,
                      factory=factory[-1], checker=checker):

            view = factory(context, request)

            # We need this in case the resource gets unwrapped and
            # needs to be rewrapped
            view.__Security_checker__ = checker

            return Proxy(view, checker)

        factory[-1] =  proxyView

        return factory

    def _call(self, require=None):
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
                discriminator = ('view', self.for_, self.name,
                                 IBrowserPresentation, self.layer),
                callable = handler,
                args = ('Views', 'provideView',
                        self.for_, self.name, IBrowserPresentation,
                        factory, self.layer),
                )
            ]


    def __call__(self):
        if not self.__pages:
            return self._call()

        # OK, we have named pages on a named view.
        # We'll replace the original class with a new subclass that
        # can traverse to the necessary pages.

        require = {}

        factory = self.factory[:]
        klass = factory[-1]

        klassdict = {'_PageTraverser__pages': {},
                     '_PageTraverser__default': self.__default,
                     '__implements__':
                     (klass.__implements__, PageTraverser.__implements__),
                     }

        for name in self.__pages:
            attribute, permission, template = self.__pages[name]

            # We need to set the default permission on pages if the pages
            # don't already have a permission explicitly set
            permission = permission or self.permission
            if permission == 'zope.Public':
                permission = CheckerPublic

            if not attribute:
                attribute = name

            require[attribute] = permission

            if template:
                klassdict[attribute] = ViewPageTemplateFile(template)

            klassdict['_PageTraverser__pages'][name] = attribute, permission

        klass = type(klass.__name__,
                     (klass, PageTraverser, object),
                     klassdict)
        factory[-1] = klass
        self.factory = factory

        permission_for_browser_publisher = self.permission
        if permission_for_browser_publisher == 'zope.Public':
            permission_for_browser_publisher = CheckerPublic
        for name in IBrowserPublisher.names(all=1):
            require[name] = permission_for_browser_publisher

        return self._call(require=require)


class PageTraverser:

    __implements__ = IBrowserPublisher

    def publishTraverse(self, request, name):
        attribute, permission = self._PageTraverser__pages[name]
        return Proxy(getattr(self, attribute),
                     NamesChecker(__call__=permission)
                     )
    publishTraverse = ContextMethod(publishTraverse)

    def browserDefault(self, request):
        return self, (self._PageTraverser__default, )
    browserDefault = ContextMethod(browserDefault)


def defaultView(_context, name, for_=None):

    if for_ is not None:
        for_ = _context.resolve(for_)

    actions = [
        Action(
        discriminator = ('defaultViewName', for_, IBrowserPresentation, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, IBrowserPresentation,
                name),
        )]

    if for_ is not None:
        actions .append(
            Action(
            discriminator = None,
            callable = handler,
            args = ('Interfaces', 'provideInterface',
                    for_.__module__+'.'+for_.__name__,
                    for_)
            )
        )

    return actions
