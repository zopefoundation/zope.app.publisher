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
"""Global Browser Menu Service

$Id$
"""
import sys
from zope.exceptions import DuplicationError
from zope.security.interfaces import Unauthorized, Forbidden
from zope.interface import implements, implementedBy
from zope.security.checker import CheckerPublic
from zope.security import checkPermission
from zope.app.component.metaconfigure import handler
from zope.app.publisher.interfaces.browser import IBrowserMenuService
from zope.app.publisher.interfaces.browser import IGlobalBrowserMenuService
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IMenuAccessView
from zope.app.publisher.browser import BrowserView
from zope.app.pagetemplate.engine import Engine
from zope.app.publication.browser import PublicationTraverser
from zope.security.proxy import ProxyFactory
from zope.app import zapi
from zope.app.component.interface import provideInterface
from zope.app.servicenames import BrowserMenu


# TODO: This was copied and trimmed down from zope.interface.
# Eventually, this will be eliminated when the browser menu
# service is changed to use adapters.
from zope.interface.interfaces import IInterface
from zope.interface import providedBy
import types
class TypeRegistry(object):

    def __init__(self):
        self._reg = {}

    def register(self, interface, object):        
        self._reg[interface] = object

    def get(self, interface, default=None):
        return self._reg.get(interface, default)

    def getAll(self, interface_spec):
        result = []
        for interface in interface_spec.__sro__:
            object = self._reg.get(interface)
            if object is not None:
                result.append(object)

        if interface_spec is not None:
            object = self._reg.get(None)
            if object is not None:
                result.append(object)

        return result

    def getAllForObject(self, object):
        return self.getAll(providedBy(object))


class MenuAccessView(BrowserView):

    implements(IMenuAccessView)

    def __getitem__(self, menu_id):
        browser_menu_service = zapi.getService(BrowserMenu)
        return browser_menu_service.getMenu(menu_id, self.context, self.request)


class Menu(object):
    """Browser menu"""

    implements(IBrowserMenu)

    def __init__(self, title, description=u''):
        self.title = title
        self.description = description
        self.registry = TypeRegistry()

    def getMenuItems(self, object=None):
        """See zope.app.publisher.interfaces.browser.IMenuItem"""
        results = []
        if object is None:
            for items in self.registry._reg.values():
                results += items
        else:
            for items in self.registry.getAllForObject(object):
                results += items
        return results


class MenuItem(object):
    """Browser menu item"""

    def __init__(self, action, title, description, filter, permission,
                 extra = None):
        self.action = action
        self.title = title
        self.description = description
        self.filter = filter
        self.permission = permission
        self.extra = extra

    def __iter__(self):
        # for backward compatability with code that thinks items are tuples
        yield self.action
        yield self.title
        yield self.description
        yield self.filter
        yield self.permission

class BaseBrowserMenuService(object):
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

        # stuff for figuring out the selected view
        request_url = request.getURL()

        for item in self.getAllMenuItems(menu_id, object):

            # Make sure we don't repeat a specification for a given title
            title = item.title
            if title in seen:
                continue
            seen[title] = 1

            if item.filter is not None:

                try:
                    include = item.filter(Engine.getContext(
                        context = object,
                        nothing = None,
                        request = request,
                        modules = ProxyFactory(sys.modules),
                        ))
                except Unauthorized:
                    include = 0

                if not include:
                    continue

            permission = item.permission
            action = item.action
            
            if permission:
                # If we have an explicit permission, check that we
                # can access it.
                if not checkPermission(permission, object):
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
                    # TODO:
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
                'description': item.description,
                'action': "%s" % action,
                'selected': selected,
                'extra': item.extra,
                })

            if len(result) >= max:
                return result

        return result

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

    def menu(self, menu_id, title, description=u''):
        s = zapi.getGlobalService(zapi.servicenames.Presentation)
        if menu_id in self._registry:
            raise DuplicationError("Menu %s is already defined." % menu_id)

        self._registry[menu_id] = Menu(title, description)

    def menuItem(self, menu_id, interface, action, title,
                 description='', filter_string=None, permission=None,
                 extra=None,
                 ):

        registry = self._registry[menu_id].registry

        if filter_string:
            filter = Engine.compile(filter_string)
        else:
            filter = None

        if permission:
            if permission == 'zope.Public':
                permission = CheckerPublic


        if interface is not None and not IInterface.providedBy(interface):
            if isinstance(interface, (type, types.ClassType)):
                interface = implementedBy(interface)
            else:
                raise TypeError(
                    "The interface argument must be an interface (or None) "
                    "or a class.")

        data = registry.get(interface) or []
        data.append(
            MenuItem(action, title, description, filter, permission, extra)
            )
        registry.register(interface, data)


def menuDirective(_context, id, title, description=''):
    _context.action(
        discriminator = ('browser:menu', id),
        callable = globalBrowserMenuService.menu,
        args = (id, title, description),
        )

def menuItemDirective(_context, menu, for_,
                      action, title, description='', filter=None,
                      permission=None, extra=None):
    return menuItemsDirective(_context, menu, for_).menuItem(
        _context, action, title, description, filter, permission, extra)


class menuItemsDirective(object):

    def __init__(self, _context, menu, for_):
        self.interface = for_
        self.menu = menu

    def menuItem(self, _context, action, title, description='',
                 filter=None, permission=None, extra=None):
        _context.action(
            discriminator = ('browser:menuItem',
                             self.menu, self.interface, title),
            callable = globalBrowserMenuService.menuItem,
            args = (self.menu, self.interface,
                    action, title, description, filter, permission, extra),
            ),

    def __call__(self, _context):
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (self.interface.__module__+'.'+self.interface.getName(),
                    self.interface)
            )
        

globalBrowserMenuService = GlobalBrowserMenuService()

_clear = globalBrowserMenuService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
