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

from zope.exceptions import DuplicationError, Unauthorized, Forbidden

from zope.configuration.action import Action

from zope.interface.type import TypeRegistry

from zope.configuration.interfaces import INonEmptyDirective
from zope.configuration.interfaces import ISubdirectiveHandler

from zope.app.services.servicenames import Interfaces

from zope.security.checker import CheckerPublic
from zope.security.management import getSecurityManager

from zope.app.security.permission import checkPermission

from zope.app.component.metaconfigure import handler, resolveInterface
from zope.app.interfaces.publisher.browser import IBrowserMenuService
from zope.app.pagetemplate.engine import Engine
from zope.app.publication.browser import PublicationTraverser

class GlobalBrowserMenuService:
    """Global Browser Menu Service
    """

    __implements__ = IBrowserMenuService

    def __init__(self):
        self._registry = {}

    _clear = __init__

    def menu(self, menu_id, title, description=''):
        # XXX we have nothing to do with the title and description. ;)

        if menu_id in self._registry:
            raise DuplicationError("Menu %s is already defined." % menu_id)

        self._registry[menu_id] = TypeRegistry()

    def menuItem(self, menu_id, interface, action, title,
                 description='', filter_string=None, permission=None,
                 ):

        registry = self._registry[menu_id]

        if filter_string:
            filter = Engine.compile(filter_string)
        else:
            filter = None

        if permission:
            if permission == 'zope.Public':
                permission = CheckerPublic
            else:
                checkPermission(None, permission)

        data = registry.get(interface) or []
        data.append((action, title, description, filter, permission))
        registry.register(interface, data)

    def getMenu(self, menu_id, object, request, max=999999):
        registry = self._registry[menu_id]
        traverser = PublicationTraverser()

        result = []
        seen = {}
        sm = getSecurityManager()

        for items in registry.getAllForObject(object):
            for action, title, description, filter, permission in items:

                # Make sure we don't repeat a specification for a given title
                if title in seen:
                    continue
                seen[title] = 1

                if filter is not None:

                    try:
                        include = filter(Engine.getContext(
                            context = object,
                            nothing = None,
                            request = request,
                            ))
                    except Unauthorized:
                        include = 0

                    if not include:
                        continue

                if permission:
                    # If we have an explicit permission, check that we
                    # can access it.
                    if not sm.checkPermission(permission, object):
                        continue

                elif action:
                    # Otherwise, test access by attempting access
                    try:
                        v = traverser.traverseRelativeURL(
                            request, object, action)
                        # XXX
                        # tickle the security proxy's checker
                        # we're assuming that view pages are callable
                        # this is a pretty sound assumption
                        v.__call__
                    except (Unauthorized, Forbidden):
                        continue # Skip unauthorized or forbidden

                if request.getURL().endswith(action):
                    selected='selected'
                else:
                    selected=''

                result.append({
                    'title': title,
                    'description': description,
                    'action': "%s" % action,
                    'selected': selected
                    })

                if len(result) >= max:
                    return result

        return result

    def getFirstMenuItem(self, menu_id, object, request):
        r = self.getMenu(menu_id, object, request, max=1)
        if r:
            return r[0]
        return None

def menuDirective(_context, id, title, description=''):
    return [Action(
        discriminator = ('browser:menu', id),
        callable = globalBrowserMenuService.menu,
        args = (id, title, description),
        )]

def menuItemDirective(_context, menu, for_,
                      action, title, description='', filter=None,
                      permission=None):
    return menuItemsDirective(_context, menu, for_).menuItem(
        _context, action, title, description, filter, permission)


class menuItemsDirective:

    __class_implements__ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    def __init__(self, _context, menu, for_):
        if for_ == '*':
            self.interface = None
        else:
            self.interface = resolveInterface(_context, for_)
        self.menu = menu

    def menuItem(self, _context, action, title, description='',
                 filter=None, permission=None):
        
        return [
            Action(
              discriminator = ('browser:menuItem',
                               self.menu, self.interface, title),
              callable = globalBrowserMenuService.menuItem,
              args = (self.menu, self.interface,
                      action, title, description, filter, permission),
              ),
                ]

    def __call__(self):
        return [
            Action(
              discriminator = None,
              callable = handler,
              args = (Interfaces, 'provideInterface',
                      self.interface.__module__+'.'+self.interface.__name__,
                      self.interface)
              )
            ]


globalBrowserMenuService = GlobalBrowserMenuService()

_clear = globalBrowserMenuService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp

__doc__ = GlobalBrowserMenuService.__doc__ + """

$Id: globalbrowsermenuservice.py,v 1.12 2003/04/09 20:51:32 philikon Exp $
"""
