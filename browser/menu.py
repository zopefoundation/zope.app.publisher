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
from zope.security import checkPermission
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
from zope.app.publisher.interfaces.browser import IMenuItemType

# Create special modules that contain all menu item types
from types import ModuleType as module
import sys
menus = module('menus')
sys.modules['zope.app.menus'] = menus


_order_counter = {}

class BrowserMenuItem(BrowserView):
    """Browser Menu Item Base Class

    >>> from zope.publisher.browser import TestRequest

    >>> class ITestInterface(Interface):
    ...     pass

    >>> from zope.publisher.interfaces.browser import IBrowserPublisher
    >>> class TestObject(object):
    ...     implements(IBrowserPublisher, ITestInterface)
    ... 
    ...     def foo(self):
    ...         pass
    ... 
    ...     def browserDefault(self, r):
    ...         return self, ()
    ... 
    ...     def publishTraverse(self, request, name):
    ...         if name.startswith('f'):
    ...             raise Forbidden, name
    ...         if name.startswith('u'):
    ...             raise Unauthorized, name
    ...         return self.foo


    Since the `BrowserMenuItem` is just a view, we can initiate it with an
    object and a request.

    >>> item = BrowserMenuItem(TestObject(), TestRequest())

    Now we add a title and description and see whether we can then access the
    value. Note that these assignments are always automatically done by the
    framework.

    >>> item.title = u'Item 1'
    >>> item.title
    u'Item 1'

    >>> item.description = u'This is Item 1.'
    >>> item.description
    u'This is Item 1.'

    >>> item.order
    0
    >>> item.order = 1
    >>> item.order
    1

    >>> item.icon is None
    True
    >>> item.icon = u'/@@/icon.png'
    >>> item.icon
    u'/@@/icon.png'

    Since there is no permission or view specified yet, the menu item should
    be available and not selected.

    >>> item.available()
    True
    >>> item.selected()
    False

    There are two ways to deny availability of a menu item: (1) the current
    user does not have the correct permission to access the action or the menu
    item itself, or (2) the filter returns `False`, in which case the menu
    item should also not be shown. 

    >>> from zope.app.testing import ztapi
    >>> from zope.app.security.interfaces import IPermission
    >>> from zope.app.security.permission import Permission
    >>> perm = Permission('perm', 'Permission')
    >>> ztapi.provideUtility(IPermission, perm, 'perm')

    >>> class ParticipationStub(object):
    ...     principal = 'principal'
    ...     interaction = None

    >>> from zope.security.management import newInteraction, endInteraction

    In the first case, the permission of the menu item was explicitely
    specified. Make sure that the user needs this permission to make the menu
    item available.

    >>> item.permission = perm

    Now, we are not setting any user. This means that the menu item should be
    available.
    
    >>> endInteraction()
    >>> newInteraction()
    >>> item.available()
    True

    Now we specify a principal that does not have the specified permission.

    >>> endInteraction()
    >>> newInteraction(ParticipationStub())
    >>> item.available()
    False

    In the second case, the permission is not explicitely defined and the
    availability is determined by the permission required to access the
    action.

    >>> item.permission = None

    All views starting with 'f' are forbidden, the ones with 'u' are
    unauthorized and all others are allowed.

    >>> item.action = u'f'
    >>> item.available()
    False
    >>> item.action = u'u'
    >>> item.available()
    False
    >>> item.action = u'a'
    >>> item.available()
    True

    Now let's test filtering. If the filter is specified, it is assumed to be
    a TALES obejct.

    >>> item.filter = Engine.compile('not:context')
    >>> item.available()
    False
    >>> item.filter = Engine.compile('context')
    >>> item.available()
    True

    Finally, make sure that the menu item can be selected.

    >>> item.request = TestRequest(SERVER_URL='http://127.0.0.1/@@view.html',
    ...                            PATH_INFO='/@@view.html')

    >>> item.selected()
    False
    >>> item.action = u'view.html'
    >>> item.selected()
    True
    >>> item.action = u'@@view.html'
    >>> item.selected()
    True
    >>> item.request = TestRequest(
    ...     SERVER_URL='http://127.0.0.1/++view++view.html',
    ...     PATH_INFO='/++view++view.html')
    >>> item.selected()
    True
    >>> item.action = u'otherview.html'
    >>> item.selected()
    False
    """
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
                # TODO:
                # tickle the security proxy's checker
                # we're assuming that view pages are callable
                # this is a pretty sound assumption
                view.__call__
            except (Unauthorized, Forbidden):
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


def getMenu(menuItemType, object, request, max=999999):
    """Return menu item entries in a TAL-friendly form.

    >>> from zope.publisher.browser import TestRequest

    >>> from zope.app.testing import ztapi
    >>> def defineMenuItem(menuItemType, for_, title, action=u'', order=0):
    ...     newclass = type(title, (BrowserMenuItem,),
    ...                     {'title':title, 'action':action, 'order':order})
    ...     classImplements(newclass, menuItemType)
    ...     ztapi.provideAdapter((for_, IBrowserRequest), menuItemType,
    ...                          newclass, title)

    >>> class IFoo(Interface): pass
    >>> class IFooBar(IFoo): pass
    >>> class IBlah(Interface): pass

    >>> class FooBar(object):
    ...     implements(IFooBar)

    >>> class Menu1(Interface): pass
    >>> class Menu2(Interface): pass

    >>> defineMenuItem(Menu1, IFoo,    'i1')
    >>> defineMenuItem(Menu1, IFooBar, 'i2')
    >>> defineMenuItem(Menu1, IBlah,   'i3')
    >>> defineMenuItem(Menu2, IFoo,    'i4')
    >>> defineMenuItem(Menu2, IFooBar, 'i5')
    >>> defineMenuItem(Menu2, IBlah,   'i6')
    >>> defineMenuItem(Menu1, IFoo,    'i7', order=-1)

    >>> items = getMenu(Menu1, FooBar(), TestRequest())
    >>> [item['title'] for item in items]
    ['i7', 'i1', 'i2']
    >>> items = getMenu(Menu2, FooBar(), TestRequest())
    >>> [item['title'] for item in items]
    ['i4', 'i5']
    >>> items = getMenu(Menu2, FooBar(), TestRequest())
    >>> [item['title'] for item in items]
    ['i4', 'i5']
    """
    result = []
    for name, item in zapi.getAdapters((object, request), menuItemType):
        if item.available():
            result.append(item)
            if len(result) >= max:
                break
        
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
    
    result = [{'title': item.title,
               'description': item.description,
               'action': item.action,
               'selected': (item.selected() and u'selected') or u'',
               'icon': item.icon,
               'extra': item.extra}
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
    """Provides a new menu (item type).

    >>> import pprint
    >>> class Context(object):
    ...     info = u'doc'
    ...     def __init__(self): self.actions = []
    ...     def action(self, **kw): self.actions.append(kw)

    Possibility 1: The Old Way
    --------------------------
    
    >>> context = Context()
    >>> menuDirective(context, u'menu1', title=u'Menu 1')
    >>> iface = context.actions[0]['args'][1]
    >>> iface.getName()
    u'menu1'
    >>> iface.getTaggedValue('title')
    u'Menu 1'
    >>> iface.getTaggedValue('description')
    u''

    >>> hasattr(sys.modules['zope.app.menus'], 'menu1')
    True

    >>> del sys.modules['zope.app.menus'].menu1

    Possibility 2: Just specify an interface
    ----------------------------------------

    >>> class menu1(Interface):
    ...     pass

    >>> context = Context()
    >>> menuDirective(context, interface=menu1)
    >>> context.actions[0]['args'][1] is menu1
    True

    Possibility 3: Specify an interface and an id
    ---------------------------------------------

    >>> context = Context()
    >>> menuDirective(context, id='menu1', interface=menu1)
    >>> context.actions[0]['args'][1] is menu1
    True
    >>> import pprint
    >>> pprint.pprint([action['discriminator'] for action in context.actions])
    [('browser', 'MenuItemType', 'zope.app.publisher.browser.menu.menu1'),
     ('interface', 'zope.app.publisher.browser.menu.menu1'),
     ('browser', 'MenuItemType', 'menu1')]
     
    Here are some disallowed configurations.

    >>> context = Context()
    >>> menuDirective(context)
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify the 'id' or 'interface' attribute.
    >>> menuDirective(context, title='Menu 1')
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify the 'id' or 'interface' attribute.
    """
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
    """Register a single menu item.

    See the `menuItemsDirective` class for tests.
    """
    return menuItemsDirective(_context, menu, for_).menuItem(
        _context, action, title, description, icon, filter,
        permission, extra, order)


class menuItemsDirective(object):
    """Register several menu items for a particular menu.

    >>> class Context(object):
    ...     info = u'doc'
    ...     def __init__(self): self.actions = []
    ...     def action(self, **kw): self.actions.append(kw)

    >>> class TestMenuItemType(Interface): pass
    >>> class ITest(Interface): pass

    >>> context = Context()
    >>> items = menuItemsDirective(context, TestMenuItemType, ITest)
    >>> context.actions
    []
    >>> items.menuItem(context, u'view.html', 'View')
    >>> context.actions[0]['args'][0]
    'provideAdapter'
    >>> len(context.actions)
    4
    """
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

        def MenuItemFactory(context, request):
            item = BrowserMenuItem(context, request)
            item.title = title
            item.description = description
            item.icon = icon
            item.action = action
            item.filter = filter
            item.permission = permission
            item.extra = extra
            item.order = order
            item._for = self.for_

            if permission is not None:
                if permission == 'zope.Public':
                    perm = CheckerPublic
                else:
                    perm = permission
                checker = InterfaceChecker(IBrowserMenuItem, perm)
                item = proxify(item, checker)

            return item
        MenuItemFactory.factory = BrowserMenuItem

        adapter(_context, (MenuItemFactory,), self.menuItemType,
                (self.for_, IBrowserRequest), name=title)
        
    def __call__(self, _context):
        # Nothing to do.
        pass
