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

$Id: metaconfigure.py,v 1.14 2003/11/21 17:10:27 jim Exp $
"""

from zope.app import zapi
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.services.servicenames import Interfaces

from zope.app.component.metaconfigure import skin, layer
from zope.app.component.metaconfigure import handler

# referred to through ZCML
from zope.app.publisher.browser.resourcemeta import resource, \
     resourceDirectory
from zope.app.publisher.browser.i18nresourcemeta import I18nResource

from zope.app.publisher.browser.viewmeta import view

def defaultView(_context, name, for_=None, **__kw):

    if __kw:
        view(_context, name=name, for_=for_, **__kw)()

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
            callable = handler,
            args = (Interfaces, 'provideInterface',
                    for_.__module__+'.'+for_.getName(),
                    for_)
            )
