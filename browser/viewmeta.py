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

$Id: viewmeta.py,v 1.9 2003/02/02 23:22:59 jack-e Exp $
"""

import os

from zope.exceptions import NotFoundError

from zope.security.proxy import Proxy
from zope.security.checker import CheckerPublic, NamesChecker, Checker
from zope.security.checker import defineChecker

from zope.configuration.interfaces import INonEmptyDirective
from zope.configuration.interfaces import ISubdirectiveHandler
from zope.configuration.action import Action
from zope.configuration.exceptions import ConfigurationError

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.publisher.browser import BrowserView

from zope.app.component.metaconfigure import handler

from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.app.security.permission import checkPermission

# from zope.proxy.context import ContextMethod, ContextAware
from zope.proxy.context import ContextMethod

from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective

# There are three cases we want to suport:
#
# Named view without pages (single-page view)
#
#     <browser:page
#         for=".IContact.IContactInfo."
#         name="info.html" 
#         template="info.pt"
#         class=".ContactInfoView."
#         permission="zope.View"
#         />
#
# Unamed view with pages (multi-page view)
#
#     <browser:pages
#         for=".IContact."
#         class=".ContactEditView."
#         permission="ZopeProducts.Contact.ManageContacts"
#         >
# 
#       <browser:page name="edit.html"       template="edit.pt" />
#       <browser:page name="editAction.html" attribute="action" />
#       </browser:pages>
#
# Named view with pages (add view is a special case of this)
#
#        <browser:view
#            name="ZopeProducts.Contact"
#            for="Zope.App.OFS.Container.IAdding."
#            class=".ContactAddView."
#            permission="ZopeProducts.Contact.ManageContacts"
#            >
#
#          <browser:page name="add.html"    template="add.pt" />
#          <browser:page name="action.html" attribute="action" />
#          </browser:view>

# We'll also provide a convenience directive for add views:
#
#        <browser:add
#            name="ZopeProducts.Contact"
#            class=".ContactAddView."
#            permission="ZopeProducts.Contact.ManageContacts"
#            >
#
#          <browser:page name="add.html"    template="add.pt" />
#          <browser:page name="action.html" attribute="action" />
#          </browser:view>

# page

def page(_context, name, permission, for_,
         layer='default', template=None, class_=None,
         allowed_interface='', allowed_attributes='',
         attribute='__call__', menu=None, title=None
         ):

    actions = _handle_menu(_context, menu, title, for_, name, permission)

    required = {}

    permission = _handle_permission(_context, permission, actions)
            
    if not (class_ or template):
        raise ConfigurationError("Must specify a class or template")

    if attribute != '__call__':
        if template:
            raise ConfigurationError(
                "Attribute and template cannot be used together.")

        if not class_:
            raise ConfigurationError(
                "A class must be provided if attribute is used")

    if template:
        template = str(_context.path(template))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)
        required['__getitem__'] = permission

    if class_:

        class_ = _context.resolve(class_)

        if attribute != '__call__':
            if not hasattr(class_, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        if template:
            template = str(_context.path(template))

            class_ = SimpleViewClass(template, bases=(class_, ))

        else:
            if not hasattr(class_, 'browserDefault'):
                cdict = {
                    'browserDefault':
                    lambda self, request:
                    (getattr(self, attribute), ())
                    }
            else:
                cdict = {}

            cdict['__page_attribute__'] = attribute
            class_ = type(class_.__name__, (class_, simple,), cdict)
            
    else:
        class_ = SimpleViewClass(template)
        
    for n in (attribute, 'browserDefault', '__call__', 'publishTraverse'):
        required[n] = permission

    _handle_allowed_interface(_context, allowed_interface, permission,
                              required, actions)
    _handle_allowed_attributes(_context, allowed_interface, permission,
                               required)
    for_ = _handle_for(_context, for_, actions)

    defineChecker(class_, Checker(required))

    actions.append(
        Action(
          discriminator = ('view', for_, name, IBrowserPresentation, layer),
          callable = handler,
          args = ('Views', 'provideView',
                  for_, name, IBrowserPresentation, [class_], layer),
          )
        )

    return actions


# pages, which are just a short-hand for multiple page directives.

# Note that a class might want to access one of the defined
# templates. If it does though, it should use getView.

def opts(**kw):
    return kw

class pages:

    __class_implements__ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    def __init__(self, _context, for_, permission,
                 layer='default', class_ = None,
                 allowed_interface='', allowed_attributes='',
                 ):
        self.opts = opts(for_=for_, permission=permission,
                         layer=layer, class_=class_,
                         allowed_interface=allowed_interface,
                         allowed_attributes=allowed_attributes,
                         )

    def page(self, _context, name, attribute='__call__', template=None,
             menu=None, title=None):
        return page(_context,
                    name=name,
                    attribute=attribute,
                    template=template,
                    menu=menu, title=title,
                    **(self.opts))

    def __call__(self):
        return ()
                    
# view (named view with pages)

# This is a different case. We actually build a class with attributes
# for all of the given pages.

class view:

    __class_implements__ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    default = None

    def __init__(self, _context, name, for_, permission,
                 layer='default', class_=None,
                 allowed_interface='', allowed_attributes='',
                 menu=None, title=None,
                 ):

        actions = _handle_menu(_context, menu, title, for_, name, permission)

        if class_:
            class_ = _context.resolve(class_)

        permission = _handle_permission(_context, permission, actions)

        self.args = (_context, name, for_, permission, layer, class_,
                     allowed_interface, allowed_attributes, actions)

        self.pages = []

    def page(self, _context, name, attribute=None, template=None):
        if template:
            template = _context.path(template)
            if not os.path.isfile(template):
                raise ConfigurationError("No such file", template)
        else:
            if not attribute:
                raise ConfigurationError(
                    "Must specify either a template or an attribute name")

        self.pages.append((name, attribute, template))
        return ()

    def defaultPage(self, _context, name):
        self.default = name
        return ()

    def __call__(self):

        (_context, name, for_, permission, layer, class_,
         allowed_interface, allowed_attributes, actions) = self.args

        required = {}
                
        cdict = {}
        pages = {}
        
        for pname, attribute, template in self.pages:
            if template:
                cdict[pname] = ViewPageTemplateFile(template)
                if attribute and attribute != name:
                    cdict[attribute] = cdict[pname]
            else:
                if not hasattr(class_, attribute):
                    raise ConfigurationError("Undefined attribute",
                                             attribute)

            attribute = attribute or pname
            required[pname] = permission

            pages[pname] = attribute
            
        if hasattr(class_, 'publishTraverse'):

            # XXX This context trickery is a hack around a problem, I
            # can't fix till after the alpha. :(

            def publishTraverse(self, request, name,
                                pages=pages, getattr=getattr):
                
                if name in pages:
                    return getattr(self, pages[name])

                m = class_.publishTraverse.__get__(self)
                return m(request, name)

            publishTraverse = ContextMethod(publishTraverse)

        else:
            def publishTraverse(self, request, name,
                                pages=pages, getattr=getattr):
                
                if name in pages:
                    return getattr(self, pages[name])
                
                raise NotFoundError(self, name, request)
            
        cdict['publishTraverse'] = publishTraverse

        if not hasattr(class_, 'browserDefault'):
            default = self.default or self.pages[0][0]
            cdict['browserDefault'] = (
                lambda self, request, default=default:
                (self, (default, ))
                )

        if class_ is not None:
            bases = (class_, simple)
        else:
            bases = (simple,)

        try:
            cname = str(name)
        except:
            cname = "GeneratedClass"

        newclass = type(cname, bases, cdict)

        for n in ('publishTraverse', 'browserDefault', '__call__'):
            required[n] = permission

        _handle_allowed_interface(_context, allowed_interface, permission,
                                  required, actions)
        _handle_allowed_attributes(_context, allowed_interface, permission,
                                   required)
        for_ = _handle_for(_context, for_, actions)

        defineChecker(newclass, Checker(required))

        actions.append(
            Action(
              discriminator = ('view',
                               for_, name, IBrowserPresentation, layer),
              callable = handler,
              args = ('Views', 'provideView',
                      for_, name, IBrowserPresentation, [newclass], layer),
              )
            )

        return actions

def addview(_context, name, permission,
            layer='default', class_=None,
            allowed_interface='', allowed_attributes='',
            menu=None, title=None,
            ):
    return view(_context, name,
                'zope.app.interfaces.container.IAdding',
                permission,
                layer, class_,
                allowed_interface, allowed_attributes,
                menu, title,
                )

addview.__implements__ = INonEmptyDirective


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

def _handle_menu(_context, menu, title, for_, name, permission):
    if menu or title:
        if not (menu and title):
            raise ConfigurationError(
                "If either menu or title are specified, they must "
                "both be specified.")

        return menuItemDirective(
            _context, menu, for_, '@@' + name, title,
            permission=permission)

    return []


def _handle_permission(_context, permission, actions):
    if permission == 'zope.Public':
        permission = CheckerPublic
    else:
        actions.append(Action(discriminator = None, callable = checkPermission,
                              args = (None, permission)))

    return permission

def _handle_allowed_interface(_context, allowed_interface, permission,
                              required, actions):
    # Allow access for all names defined by named interfaces
    if allowed_interface.strip():
        for i in allowed_interface.strip().split():
            i = _context.resolve(i)
            actions .append(
                Action(discriminator = None, callable = handler,
                       args = ('Interfaces', 'provideInterface', None, i)
                       ))
            for name in i:
                required[name] = permission

def _handle_allowed_attributes(_context, allowed_attributes, permission,
                               required):
    # Allow access for all named attributes
    if allowed_attributes.strip():
        for name in allowed_attributes.strip().split():
            required[name] = permission

def _handle_for(_context, for_, actions):
    if for_ == '*':
        for_ = None
        
    if for_ is not None:
        for_ = _context.resolve(for_)
        
        actions .append(
            Action(discriminator = None, callable = handler,
                   args = ('Interfaces', 'provideInterface', None, for_)
            ))

    return for_

# class simple(ContextAware, BrowserView):
class simple(BrowserView):
    __implements__ = IBrowserPublisher, BrowserView.__implements__

    def publishTraverse(self, request, name):
        raise NotFoundError(self, name, request)

    def __call__(self, *a, **k):
        # If a class doesn't provide it's own call, then get the attribute
        # given by the browser default.

        attr = self.__page_attribute__
        if attr == '__call__':
            raise AttributeError("__call__")

        meth = getattr(self, attr)
        return meth(*a, **k)
    
        
        
