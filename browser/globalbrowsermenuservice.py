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
"""Global Browser Menu Service

$Id: globalbrowsermenuservice.py,v 1.26 2003/09/24 01:52:33 garrett Exp $
"""
__metaclass__ = type 

import sys
from zope.exceptions import DuplicationError, Unauthorized, Forbidden
from zope.interface.type import TypeRegistry
from zope.interface import implements
from zope.app.services.servicenames import Interfaces
from zope.security.checker import CheckerPublic
from zope.security.management import getSecurityManager
from zope.app.security.permission import checkPermission
from zope.app.component.metaconfigure import handler
from zope.app.interfaces.publisher.browser import \
     IBrowserMenuService, IGlobalBrowserMenuService, IBrowserMenu
from zope.app.pagetemplate.engine import Engine
from zope.app.publication.browser import PublicationTraverser
from zope.security.proxy import ProxyFactory

class Menu:
    """Browser menu"""

    implements(IBrowserMenu)

    def __init__(self, title, description=u'', usage=u''):
        self.title = title
        self.description = description
        self.usage = usage
        self.registry = TypeRegistry()

    def getMenuItems(self, object=None):
        """See zope.app.interfaces.publisher.browser.IMenuItem"""
        results = []
        if object is None:
            for items in self.registry._reg.values():
                results += items
        else:
            for items in self.registry.getAllForObject(object):
                results += items
        return results


class BaseBrowserMenuService:
    """Global Browser Menu Service"""

    implements(IBrowserMenuService)

    def __init__(self):
        self._registry = {}

    def getAllMenuItems(self, menu_id, object):
        return self._registry[menu_id].getMenuItems(object)

    def getMenu(self, menu_id, object, request, max=999999):
        traverser = PublicationTraverser()

        result = []
        seen = {}
        sm = getSecurityManager()

        # stuff for figuring out the selected view
        request_url = request.getURL()

        for items in self.getAllMenuItems(menu_id, object):
            action, title, description, filter, permission = items

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
                        modules = ProxyFactory(sys.modules),
                        ))
                except Unauthorized:
                    include = 0

                if not include:
                    continue

            if permission:
                # If we have an explicit permission, check that we
                # can access it.
                if not sm.checkPermission(permission, object) and \
                       permission is not CheckerPublic:
                    continue

            elif action:
                # Otherwise, test access by attempting access
                path = action
                l = action.find('?')
                if l >= 0:
                   path = action[:l]
                try:
                    v = traverser.traverseRelativeURL(
                        request, object, path)
                    # XXX
                    # tickle the security proxy's checker
                    # we're assuming that view pages are callable
                    # this is a pretty sound assumption
                    v.__call__
                except (Unauthorized, Forbidden):
                    continue # Skip unauthorized or forbidden

            normalized_action = action
            if action.startswith('@@'):
                normalized_action = action[2:]

            if request_url.endswith('/'+normalized_action):
                selected='selected'
            elif request_url.endswith('/++view++'+normalized_action):
                selected='selected'
            elif request_url.endswith('/@@'+normalized_action):
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

    def getMenuUsage(self, menu_id):
        return self._registry[menu_id].usage


    def getFirstMenuItem(self, menu_id, object, request):
        r = self.getMenu(menu_id, object, request, max=1)
        if r:
            return r[0]
        return None


class GlobalBrowserMenuService(BaseBrowserMenuService):
    """Global Browser Menu Service that can be manipulated by adding new menus
    and menu entries."""

    implements(IGlobalBrowserMenuService)

    def __init__(self):
        self._registry = {}

    _clear = __init__

    def menu(self, menu_id, title, description=u'', usage=u''):
        # XXX we have nothing to do with the title and description. ;)

        if menu_id in self._registry:
            raise DuplicationError("Menu %s is already defined." % menu_id)

        self._registry[menu_id] = Menu(title, description, usage)

    def menuItem(self, menu_id, interface, action, title,
                 description='', filter_string=None, permission=None,
                 ):

        registry = self._registry[menu_id].registry

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


def menuDirective(_context, id, title, description='', usage=u''):
    _context.action(
        discriminator = ('browser:menu', id),
        callable = globalBrowserMenuService.menu,
        args = (id, title, description, usage),
        )

def menuItemDirective(_context, menu, for_,
                      action, title, description='', filter=None,
                      permission=None):
    return menuItemsDirective(_context, menu, for_).menuItem(
        _context, action, title, description, filter, permission)


class menuItemsDirective:

    def __init__(self, _context, menu, for_):
        self.interface = for_
        self.menu = menu

    def menuItem(self, _context, action, title, description='',
                 filter=None, permission=None):
        _context.action(
            discriminator = ('browser:menuItem',
                             self.menu, self.interface, title),
            callable = globalBrowserMenuService.menuItem,
            args = (self.menu, self.interface,
                    action, title, description, filter, permission),
            ),

    def __call__(self, _context):
        _context.action(
            discriminator = None,
            callable = handler,
            args = (Interfaces, 'provideInterface',
                    self.interface.__module__+'.'+self.interface.getName(),
                    self.interface)
            )

globalBrowserMenuService = GlobalBrowserMenuService()

_clear = globalBrowserMenuService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
