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

$Id: viewmeta.py,v 1.2 2002/12/25 14:13:09 jim Exp $
"""

# XXX this will need to be refactored soon. :)

from zope.security.proxy import Proxy
from zope.security.checker import CheckerPublic, NamesChecker

from zope.interfaces.configuration import INonEmptyDirective
from zope.interfaces.configuration import ISubdirectiveHandler
from zope.configuration.action import Action
from zope.configuration.exceptions import ConfigurationError

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.component.metaconfigure import handler

from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.app.publisher.browser.resourcemeta import resource

from zope.proxy.context import ContextMethod


class view(resource):

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

        resource.__init__(self, _context, factory, name, layer,
                          permission, allowed_interface, allowed_attributes)

        if name:
            self.__pages = {}


    def page(self, _context, name, attribute=None, permission=None,
             layer=None, template=None):

        if self.template:
            raise ConfigurationError(
                "Can't use page or defaultPage subdirectives for simple "
                "template views")

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

            # Call super(view, self).page() in order to get the side
            # effects. (At the time of writing, this is to increment
            # self.pages by one.)
            # Throw away the result, as all the pages are accessed by
            # traversing the PageTraverser subclass.
            super(view, self).page(_context, name, attribute)
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

        return super(view, self).page(
            _context, name, attribute, permission, layer,
            factory=factory)

    def defaultPage(self, _context, name):
        if self.name:
            self.__default = name
            return ()

        return [Action(
            discriminator = ('defaultViewName', self.for_, self.type, name),
            callable = handler,
            args = ('Views','setDefaultViewName', self.for_, self.type, name),
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

    def _discriminator(self, name, layer):
        return ('view', self.for_, name, self.type, layer)

    def _args(self, name, factory, layer):
        return ('Views', 'provideView',
                self.for_, name, self.type, factory, layer)

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

    def __call__(self):
        if not self.__pages:
            return super(view, self).__call__()

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

        return super(view, self).__call__(require=require)


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


def defaultView(_context, name, for_=None, **__kw):

    if __kw:
        actions = view(_context, name=name, for_=for_, **__kw)()
    else:
        actions = []

    if for_ is not None:
        for_ = _context.resolve(for_)

    type = IBrowserPresentation

    actions += [
        Action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        )]

    if for_ is not None:
        actions += [
        Action(
        discriminator = None,
        callable = handler,
        args = ('Interfaces', 'provideInterface',
                for_.__module__+'.'+for_.__name__,
                for_)
        )
        ]

    return actions
