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

$Id: viewmeta.py,v 1.25 2003/05/27 14:18:22 jim Exp $
"""

from zope.interface import classProvides, directlyProvides
import os

from zope.interface.implements import implements
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.exceptions import NotFoundError

from zope.security.checker import CheckerPublic, Checker
from zope.security.checker import defineChecker

from zope.configuration.interfaces import INonEmptyDirective
from zope.configuration.interfaces import ISubdirectiveHandler
from zope.configuration.action import Action
from zope.configuration.exceptions import ConfigurationError

from zope.app.services.servicenames import Interfaces, Views

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.publisher.browser import BrowserView

from zope.app.component.metaconfigure import handler, resolveInterface

from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.app.security.permission import checkPermission

from zope.context import ContextMethod

from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective, globalBrowserMenuService

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
         attribute='__call__', menu=None, title=None, 
         usage=u''
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
        template = os.path.abspath(str(_context.path(template)))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)
        required['__getitem__'] = permission

    if class_:
        original_class = _context.resolve(class_)

        if attribute != '__call__':
            if not hasattr(original_class, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        if template:
            # class and template
            new_class = SimpleViewClass(
                template, bases=(original_class, ), usage=usage
                )
        else:
            if not hasattr(original_class, 'browserDefault'):
                cdict = {
                    'browserDefault':
                    ContextMethod(lambda self, request:
                                  (getattr(self, attribute), ())
                                  )
                    }
            else:
                cdict = {}

            cdict['__page_attribute__'] = attribute
            new_class = type(original_class.__name__,
                          (original_class, simple,),
                          cdict)
            new_class.usage = usage              

        if hasattr(original_class, '__implements__'):
            implements(new_class, IBrowserPublisher)
            implements(new_class, IBrowserPresentation, check=False)

    else:
        # template
        new_class = SimpleViewClass(template, usage=usage)

    for n in (attribute, 'browserDefault', '__call__', 'publishTraverse'):
        required[n] = permission

    _handle_allowed_interface(_context, allowed_interface, permission,
                              required, actions)
    _handle_allowed_attributes(_context, allowed_interface, permission,
                               required)
    for_ = _handle_for(_context, for_, actions)

    defineChecker(new_class, Checker(required))

    actions.append(
        Action(
          discriminator = ('view', for_, name, IBrowserPresentation, layer),
          callable = handler,
          args = (Views, 'provideView',
                  for_, name, IBrowserPresentation, [new_class], layer),
          )
        )

    if not usage and menu:
        actions.append(
            Action(discriminator = None,
            callable = _handle_usage_from_menu,
            args = (new_class, menu, ),
            )
        )

    return actions


# pages, which are just a short-hand for multiple page directives.

# Note that a class might want to access one of the defined
# templates. If it does though, it should use getView.

def opts(**kw):
    return kw

class pages:

    classProvides(INonEmptyDirective)
    __implements__ = ISubdirectiveHandler

    def __init__(self, _context, for_, permission,
                 layer='default', class_=None,
                 allowed_interface='', allowed_attributes='',
                 ):
        self.opts = opts(for_=for_, permission=permission,
                         layer=layer, class_=class_,
                         allowed_interface=allowed_interface,
                         allowed_attributes=allowed_attributes,
                         )

    def page(self, _context, name, attribute='__call__', template=None,
             menu=None, title=None, usage=u''):
        return page(_context,
                    name=name,
                    attribute=attribute,
                    template=template,
                    menu=menu, title=title,
                    usage=usage,
                    **(self.opts))

    def __call__(self):
        return ()

# view (named view with pages)

# This is a different case. We actually build a class with attributes
# for all of the given pages.

class view:

    classProvides(INonEmptyDirective)
    __implements__ = ISubdirectiveHandler

    default = None

    def __init__(self, _context, name, for_, permission,
                 layer='default', class_=None,
                 allowed_interface='', allowed_attributes='',
                 menu=None, title=None, usage=u''
                 ):

        actions = _handle_menu(_context, menu, title, for_, name, permission)

        if class_:
            class_ = _context.resolve(class_)

        permission = _handle_permission(_context, permission, actions)

        self.args = (_context, name, for_, permission, layer, class_,
                     allowed_interface, allowed_attributes, actions)

        self.pages = []
        # default usage is u''
        self.usage = usage
        self.menu = menu

    def page(self, _context, name, attribute=None, template=None, usage=None):
        if template:
            template = os.path.abspath(_context.path(template))
            if not os.path.isfile(template):
                raise ConfigurationError("No such file", template)
        else:
            if not attribute:
                raise ConfigurationError(
                    "Must specify either a template or an attribute name")

        self.pages.append((name, attribute, template, usage))
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

        for pname, attribute, template, usage in self.pages:
            if usage is None:
                # If no usage is declared explicitly for this page, use the
                # usage given for the whole view.
                usage = self.usage
            if template:
                cdict[pname] = ViewPageTemplateFile(template, usage=usage)
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

        else:
            def publishTraverse(self, request, name,
                                pages=pages, getattr=getattr):

                if name in pages:
                    return getattr(self, pages[name])

                raise NotFoundError(self, name, request)

        cdict['publishTraverse'] = ContextMethod(publishTraverse)

        if not hasattr(class_, 'browserDefault'):
            if self.default or self.pages:
                default = self.default or self.pages[0][0]
                cdict['browserDefault'] = ContextMethod(
                    lambda self, request, default=default:
                    (self, (default, ))
                    )
            elif providesCallable(class_):
                cdict['browserDefault'] = ContextMethod(
                    lambda self, request: (self, ())
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
              args = (Views, 'provideView',
                      for_, name, IBrowserPresentation, [newclass], layer),
              )
            )

        return actions

def addview(_context, name, permission,
            layer='default', class_=None,
            allowed_interface='', allowed_attributes='',
            menu=None, title=None, usage=u'',
            ):
    return view(_context, name,
                'zope.app.interfaces.container.IAdding',
                permission,
                layer, class_,
                allowed_interface, allowed_attributes,
                menu, title, usage
                )

directlyProvides(addview, INonEmptyDirective)


def defaultView(_context, name, for_=None):

    if for_ is not None:
        for_ = resolveInterface(_context, for_)

    actions = [
        Action(
        discriminator = ('defaultViewName', for_, IBrowserPresentation, name),
        callable = handler,
        args = (Views,'setDefaultViewName', for_, IBrowserPresentation,
                name),
        )]

    if for_ is not None:
        actions .append(
            Action(
            discriminator = None,
            callable = handler,
            args = (Interfaces, 'provideInterface',
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
            i = resolveInterface(_context, i)
            actions .append(
                Action(discriminator = None, callable = handler,
                       args = (Interfaces, 'provideInterface', None, i)
                       ))
            for name in i:
                required[name] = permission

def _handle_allowed_attributes(_context, allowed_attributes, permission,
                               required):
    # Allow access for all named attributes
    if allowed_attributes.strip():
        for name in allowed_attributes.strip().split():
            required[name] = permission

def _handle_usage_from_menu(view, menu_id):
    usage = globalBrowserMenuService.getMenuUsage(menu_id)
    view.usage = usage

def _handle_for(_context, for_, actions):
    if for_ == '*':
        for_ = None

    if for_ is not None:
        for_ = resolveInterface(_context, for_)

        actions .append(
            Action(discriminator = None, callable = handler,
                   args = (Interfaces, 'provideInterface', None, for_)
            ))

    return for_

class simple(BrowserView):
    __implements__ = IBrowserPublisher, BrowserView.__implements__

    def publishTraverse(self, request, name):
        raise NotFoundError(self, name, request)
    publishTraverse = ContextMethod(publishTraverse)

    def __call__(self, *a, **k):
        # If a class doesn't provide it's own call, then get the attribute
        # given by the browser default.

        attr = self.__page_attribute__
        if attr == '__call__':
            raise AttributeError("__call__")

        meth = getattr(self, attr)
        return meth(*a, **k)
    __call__ = ContextMethod(__call__)

def providesCallable(class_):
    if hasattr(class_, '__call__'):
        for c in class_.__mro__:
            if '__call__' in c.__dict__:
                return True
    return False
