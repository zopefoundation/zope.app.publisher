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

$Id: metaconfigure.py,v 1.9 2003/08/02 07:04:09 philikon Exp $
"""

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.services.servicenames import Interfaces

from zope.app.component.metaconfigure import skin as _skin
from zope.app.component.metaconfigure import handler

# referred to through ZCML
from zope.app.publisher.browser.resourcemeta import resource
from zope.app.publisher.browser.i18nresourcemeta import I18nResource

from zope.app.publisher.browser.viewmeta import view

def skin(_context, **__kw):
    return _skin(_context, type=IBrowserPresentation, **__kw)

def defaultView(_context, name, for_=None, **__kw):

    if __kw:
        view(_context, name=name, for_=for_, **__kw)()

    type = IBrowserPresentation

    _context.action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = handler,
            args = (Interfaces, 'provideInterface',
                    for_.__module__+'.'+for_.__name__,
                    for_)
            )
