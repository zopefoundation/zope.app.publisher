##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Menu Registration code.

$Id$
"""
__docformat__ = "reStructuredText"
from zope.component.interfaces import IFactory
from zope.configuration.exceptions import ConfigurationError

from zope.interface import Interface, implements, classImplements
from zope.interface import directlyProvides, providedBy
from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security import checkPermission, canAccess
from zope.security.checker import InterfaceChecker, CheckerPublic
from zope.security.interfaces import Unauthorized, Forbidden
from zope.security.proxy import ProxyFactory, removeSecurityProxy

from zope.app import zapi
from zope.app.component.interface import provideInterface
from zope.app.component.metaconfigure import adapter, proxify
from zope.app.pagetemplate.engine import Engine
from zope.app.publication.browser import PublicationTraverser
from zope.app.publisher.browser import BrowserView
from zope.app.publisher.interfaces.browser import IMenuAccessView
from zope.app.publisher.interfaces.browser import IBrowserMenuItem
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem
from zope.app.publisher.interfaces.browser import IMenuItemType

# Create special modules that contain all menu item types
from types import ModuleType as module
import sys
menus = module('menus')
sys.modules['zope.app.menus'] = menus


_order_counter = {}

class BrowserMenuItem(BrowserView):
    """Browser Menu Item Class"""
    implements(IBrowserMenuItem)

    # See zope.app.publisher.interfaces.browser.IBrowserMenuItem
    title = u''
    description = u''
    action = u''
    extra = None
    order = 0
    permission = None
    filter = None
    icon = None
    _for = Interface

    def available(self):
        """See zope.app.publisher.interfaces.browser.IBrowserMenuItem"""
        # Make sure we have the permission needed to access the menu's action
        if self.permission is not None:
            # If we have an explicit permission, check that we
            # can access it.
            if not checkPermission(self.permission, self.context):
                return False

        elif self.action != u'':
            # Otherwise, test access by attempting access
            path = self.action
            l = self.action.find('?')
            if l >= 0:
                path = self.action[:l]

            traverser = PublicationTraverser()
            try:
                view = traverser.traverseRelativeURL(
                    self.request, self.context, path)
            except (Unauthorized, Forbidden):
                return False
            else:
                # we're assuming that view pages are callable
                # this is a pretty sound assumption
                if not canAccess(view, '__call__'):
                    return False

        # Make sure that we really want to see this menu item
        if self.filter is not None:

            try:
                include = self.filter(Engine.getContext(
                    context = self.context,
                    nothing = None,
                    request = self.request,
                    modules = ProxyFactory(sys.modules),
                    ))
            except Unauthorized:
                return False
            else:
                if not include:
                    return False

        return True
        

    def selected(self):
        """See zope.app.publisher.interfaces.browser.IBrowserMenuItem"""
        request_url = self.request.getURL()

        normalized_action = self.action
        if self.action.startswith('@@'):
            normalized_action = self.action[2:]

        if request_url.endswith('/'+normalized_action):
            return True
        if request_url.endswith('/++view++'+normalized_action):
            return True
        if request_url.endswith('/@@'+normalized_action):
            return True

        return False


class BrowserSubMenuItem(BrowserMenuItem):
    """Browser Menu Item Base Class"""
    implements(IBrowserSubMenuItem)

    # See zope.app.publisher.interfaces.browser.IBrowserSubMenuItem
    submenuType = None

    def selected(self):
        """See zope.app.publisher.interfaces.browser.IBrowserMenuItem"""
        if self.action is u'':
            return False
        return super(BrowserSubMenuItem, self).selected()


def getMenu(menuItemType, object, request):
    """Return menu item entries in a TAL-friendly form."""
    result = []
    for name, item in zapi.getAdapters((object, request), menuItemType):
        if item.available():
            result.append(item)
        
    # Now order the result. This is not as easy as it seems.
    #
    # (1) Look at the interfaces and put the more specific menu entries to the
    #     front.
    # (2) Sort unabigious entries by order and then by title.
    ifaces = list(providedBy(removeSecurityProxy(object)).__iro__)
    result = [
        (ifaces.index(item._for or Interface), item.order, item.title, item)
        for item in result]
    result.sort()
    
    result = [
        {'title': item.title,
         'description': item.description,
         'action': item.action,
         'selected': (item.selected() and u'selected') or u'',
         'icon': item.icon,
         'extra': item.extra,
         'submenu': (IBrowserSubMenuItem.providedBy(item) and
                     getMenu(item.submenuType, object, request)) or None}
        for index, order, title, item in result]
    return result


def getFirstMenuItem(menuItemType, object, request):
    """Get the first item of a menu."""
    items = getMenu(menuItemType, object, request)
    if items:
        return items[0]
    return None


class MenuAccessView(BrowserView):
    """A view allowing easy access to menus."""
    implements(IMenuAccessView)

    def __getitem__(self, typeString):
        # Convert the menu item type identifyer string to the type interface
        menuItemType = zapi.getUtility(IMenuItemType, typeString)
        return getMenu(menuItemType, self.context, self.request)


def menuDirective(_context, id=None, interface=None,
                  title=u'', description=u''):
    """Provides a new menu (item type)."""
    if id is None and interface is None: 
        raise ConfigurationError(
            "You must specify the 'id' or 'interface' attribute.")

    if interface is None:
        interface = InterfaceClass(id, (),
                                   __doc__='Menu Item Type: %s' %id,
                                   __module__='zope.app.menus')
        # Add the menu item type to the `menus` module.
        # Note: We have to do this immediately, so that directives using the
        # MenuField can find the menu item type.
        setattr(menus, id, interface)
        path = 'zope.app.menus.' + id
    else:
        path = interface.__module__ + '.' + interface.getName()

        # If an id was specified, make this menu available under this id.
        # Note that the menu will be still available under its path, since it
        # is an adapter, and the `MenuField` can resolve paths as well.
        if id is None:
            id = path
        else:
            # Make the interface available in the `zope.app.menus` module, so
            # that other directives can find the interface under the name
            # before the CA is setup.
            _context.action(
                discriminator = ('browser', 'MenuItemType', path),
                callable = provideInterface,
                args = (path, interface, IMenuItemType, _context.info)
                )
            setattr(menus, id, interface)

    # Set the title and description of the menu item type
    interface.setTaggedValue('title', title)
    interface.setTaggedValue('description', description)

    # Register the layer interface as an interface
    _context.action(
        discriminator = ('interface', path),
        callable = provideInterface,
        args = (path, interface),
        kw = {'info': _context.info}
        )

    # Register the menu item type interface as an IMenuItemType
    _context.action(
        discriminator = ('browser', 'MenuItemType', id),
        callable = provideInterface,
        args = (id, interface, IMenuItemType, _context.info)
        )


def menuItemDirective(_context, menu, for_,
                      action, title, description=u'', icon=None, filter=None,
                      permission=None, extra=None, order=0):
    """Register a single menu item."""
    return menuItemsDirective(_context, menu, for_).menuItem(
        _context, action, title, description, icon, filter,
        permission, extra, order)


def subMenuItemDirective(_context, menu, for_, title, submenu,
                         action=u'', description=u'', icon=None, filter=None,
                         permission=None, extra=None, order=0):
    """Register a single sub-menu menu item."""
    return menuItemsDirective(_context, menu, for_).subMenuItem(
        _context, submenu, title, description, action, icon, filter,
        permission, extra, order)


class MenuItemFactory(object):
    """generic factory for menu items."""

    def __init__(self, factory, **kwargs):
        self.factory = factory
        if 'permission' in kwargs and kwargs['permission'] == 'zope.Public':
            kwargs['permission'] = CheckerPublic
        self.kwargs = kwargs
    
    def __call__(self, context, request):
        item = self.factory(context, request)

        for key, value in self.kwargs.items():
            setattr(item, key, value)

        if item.permission is not None:
            checker = InterfaceChecker(IBrowserMenuItem, item.permission)
            item = proxify(item, checker)

        return item


class menuItemsDirective(object):
    """Register several menu items for a particular menu."""

    def __init__(self, _context, menu, for_):
        self.for_ = for_
        self.menuItemType = menu

    def menuItem(self, _context, action, title, description=u'',
                 icon=None, filter=None, permission=None, extra=None, order=0):

        if filter is not None:
            filter = Engine.compile(filter)

        if order == 0:
            order = _order_counter.get(self.for_, 1)
            _order_counter[self.for_] = order + 1

        factory = MenuItemFactory(
            BrowserMenuItem,
            title=title, description=description, icon=icon, action=action,
            filter=filter, permission=permission, extra=extra, order=order,
            _for=self.for_)
        adapter(_context, (factory,), self.menuItemType,
                (self.for_, IBrowserRequest), name=title)

    def subMenuItem(self, _context, submenu, title, description=u'',
                    action=u'', icon=None, filter=None, permission=None,
                    extra=None, order=0):

        if filter is not None:
            filter = Engine.compile(filter)

        if order == 0:
            order = _order_counter.get(self.for_, 1)
            _order_counter[self.for_] = order + 1

        factory = MenuItemFactory(
            BrowserSubMenuItem,
            title=title, description=description, icon=icon, action=action,
            filter=filter, permission=permission, extra=extra, order=order,
            _for=self.for_, submenuType=submenu)
        adapter(_context, (factory,), self.menuItemType,
                (self.for_, IBrowserRequest), name=title)
        
    def __call__(self, _context):
        # Nothing to do.
        pass
