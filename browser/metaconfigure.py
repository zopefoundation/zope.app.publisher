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

$Id: metaconfigure.py,v 1.10 2003/08/02 09:11:21 anthony Exp $
"""

from zope.configuration.action import Action

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.services.servicenames import Interfaces

from zope.app.component.metaconfigure import skin as _skin
from zope.app.component.metaconfigure import handler, resolveInterface

# referred to through ZCML
from zope.app.publisher.browser.resourcemeta import resource
from zope.app.publisher.browser.i18nresourcemeta import I18nResource

from zope.app.publisher.browser.viewmeta import view

def skin(_context, **__kw):
    return _skin(_context,
                 type='zope.publisher.interfaces.browser.IBrowserPresentation',
                 **__kw)

def defaultView(_context, name, for_=None, **__kw):

    if __kw:
        actions = view(_context, name=name, for_=for_, **__kw)()
    else:
        actions = []

    if for_ is not None:
        for_ = resolveInterface(_context, for_)

    type = IBrowserPresentation

    actions += [
        Action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        )
        ]
    if for_ is not None:
        actions.append
        (
        Action(
        discriminator = None,
        callable = handler,
        args = (Interfaces, 'provideInterface',
                for_.__module__+'.'+for_.__name__,
                for_)
              )
        )


    return actions
