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
"""Browser configuration code

$Id$
"""
from zope.component.interfaces import IDefaultViewName
from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces.browser import ILayer, ISkin, IDefaultSkin
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.app import zapi
from zope.app.component.metaconfigure import handler
from zope.app.container.interfaces import IAdding
from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective
from zope.app.component.contentdirective import ContentDirective

# referred to through ZCML
from zope.app.publisher.browser.resourcemeta import resource
from zope.app.publisher.browser.resourcemeta import resourceDirectory
from zope.app.publisher.browser.i18nresourcemeta import I18nResource
from zope.app.publisher.browser.viewmeta import view
from zope.app.component.interface import provideInterface

from zope.app.component.interface import provideInterface

# Create special modules that contain all layers and skins
from types import ModuleType as module
import sys
layers = module('layers')
sys.modules['zope.app.layers'] = layers

skins = module('skins')
sys.modules['zope.app.skins'] = skins


def layer(_context, name, base=IBrowserRequest):
    if ',' in name:
        raise TypeError("Commas are not allowed in layer names.")

    layer = InterfaceClass(name, (base, ),
                           __doc__='Layer: %s' %name,
                           __module__='zope.app.layers')

    # Add the layer to the skins module.
    # Note: We have to do this immediately, so that directives using the
    # InterfaceField can find the layer.
    setattr(layers, name, layer)

    # Register the layer interface as an interface
    _context.action(
        discriminator = ('interface', 'zope.app.layers.'+name),
        callable = provideInterface,
        args = ('zope.app.layers.'+name, layer),
        kw = {'info': _context.info}
        )

    # Register the layer interface as a layer
    _context.action(
        discriminator = ('layer', name),
        callable = provideInterface,
        args = (name, layer, ILayer, _context.info)
        )

def skin(_context, name, layers):

    skin = InterfaceClass(name, layers,
                          __doc__='Skin: %s' %name,
                          __module__='zope.app.skins')

    # Register the layer interface as an interface
    # Note: We have to do this immediately, so that directives using the
    # InterfaceField can find the layer.
    _context.action(
        discriminator = ('interface', 'zope.app.skins.'+name),
        callable = provideInterface,
        args = ('zope.app.skins.'+name, skin),
        kw = {'info': _context.info}
        )

    # Register the layer interface as a layer
    _context.action(
        discriminator = ('skin', name),
        callable = provideInterface,
        args = (name, skin, ISkin, _context.info)
        )

def setDefaultSkin(name, info):
    # XXX: Test
    skin = zapi.getUtility(ISkin, name)
    handler('Adapters', 'register',
            (IBrowserRequest,), IDefaultSkin, '', skin, info),

def defaultSkin(_context, name):

    _context.action(
        discriminator = 'defaultSkin',
        callable = setDefaultSkin,
        args = (name, _context.info)
        )

def defaultView(_context, name, for_=None):

    type = IBrowserRequest

    _context.action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = (zapi.servicenames.Adapters, 'register',
                (for_, type), IDefaultViewName, '', name, _context.info)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )


def addMenuItem(_context, title, class_=None, factory=None, description='',
                permission=None, filter=None, view=None):
    """Create an add menu item for a given class or factory

    As a convenience, a class can be provided, in which case, a
    factory is automatically defined based on the class.  In this
    case, the factory id is based on the class name.

    """
    
    if class_ is None:
        if factory is None:
            raise ValueError("Must specify either class or factory")
    else:
        if factory is not None:
            raise ValueError("Can't specify both class and factory")
        if permission is None:
            raise ValueError(
                "A permission must be specified when a class is used")
        factory = "zope.app.browser.add.%s.%s" % (
            class_.__module__, class_.__name__) 
        ContentDirective(_context, class_).factory(
            _context,
            id = factory)

    extra = {'factory': factory}

    if view:
        action = view
    else:
        action = factory

    menuItemDirective(_context, 'zope.app.container.add', IAdding,
                      action, title, description, filter,
                      permission, extra)
