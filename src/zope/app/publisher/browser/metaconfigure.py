##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
__docformat__ = 'restructuredtext'

import warnings
from zope import component
from zope.component.interface import provideInterface
from zope.component.zcml import handler
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultSkin

# referred to through ZCML
from zope.app.publisher.browser.resourcemeta import resource
from zope.app.publisher.browser.resourcemeta import resourceDirectory
from zope.app.publisher.browser.i18nresourcemeta import I18nResource
from zope.app.publisher.browser.viewmeta import view


def setDefaultSkin(name, info=''):
    """Set the default skin.

    >>> from zope.interface import directlyProvides
    >>> from zope.app.testing import ztapi

    >>> class Skin1: pass
    >>> directlyProvides(Skin1, IBrowserSkinType)

    >>> ztapi.provideUtility(IBrowserSkinType, Skin1, 'Skin1')
    >>> setDefaultSkin('Skin1')
    >>> adapters = component.getSiteManager().adapters

	Lookup the default skin for a request that has the

    >>> adapters.lookup((IBrowserRequest,), IDefaultSkin, '') is Skin1
    True
    """
    skin = component.getUtility(IBrowserSkinType, name)
    handler('registerAdapter',
            skin, (IBrowserRequest,), IDefaultSkin, '', info),

def defaultSkin(_context, name):

    _context.action(
        discriminator = 'defaultSkin',
        callable = setDefaultSkin,
        args = (name, _context.info)
        )

def defaultView(_context, name, for_=None, layer=IBrowserRequest):

    _context.action(
        discriminator = ('defaultViewName', for_, layer, name),
        callable = handler,
        args = ('registerAdapter',
                name, (for_, layer), IDefaultViewName, '', _context.info)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )
