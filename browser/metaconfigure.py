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

$Id$
"""

from zope.app import zapi
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.component.metaconfigure import skin, layer
from zope.app.component.metaconfigure import handler
from zope.app.container.interfaces import IAdding
from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective
from zope.app.component.contentdirective import ContentDirective

# referred to through ZCML
from zope.app.publisher.browser.resourcemeta import resource, \
     resourceDirectory
from zope.app.publisher.browser.i18nresourcemeta import I18nResource
from zope.app.publisher.browser.viewmeta import view
from zope.app.component.interface import provideInterface

def defaultView(_context, name, for_=None):

    type = IBrowserRequest

    _context.action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = (zapi.servicenames.Presentation,
                'setDefaultViewName', for_, type, name),
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )


_next_id = 0
def addMenuItem(_context, title, class_=None, factory=None, description='',
                permission=None, filter=None, view=None):
    """Create an add menu item for a given class or factory

    As a convenience, a class can be provided, in which case, a factory is
    automatically defined baded on the class.
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
        global _next_id
        _next_id += 1
        factory = "zope.app.browser.add.%s.f%s" % (
            class_.__name__, _next_id) 
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


def test_reset():
    global _next_id
    _next_id = 0
    
from zope.testing.cleanup import addCleanUp
addCleanUp(test_reset)
