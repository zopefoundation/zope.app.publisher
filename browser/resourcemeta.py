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

$Id: resourcemeta.py,v 1.8 2003/08/02 07:04:09 philikon Exp $
"""

from zope.security.checker import CheckerPublic, NamesChecker
from zope.configuration.exceptions import ConfigurationError
from zope.app.services.servicenames import Resources
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.component.metaconfigure import handler

from fileresource import FileResourceFactory, ImageResourceFactory

allowed_names = ('GET', 'HEAD', 'publishTraverse', 'browserDefault',
                 'request', '__call__')

def resource(_context, name, layer='default', permission='zope.Public',
             file=None, image=None):

    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names, permission)

    if file and image or not (file or image):
        raise ConfigurationError(
            "Must use exactly one of file or image "
            "attributes for resource directives"
            )

    if file:
        factory = FileResourceFactory(_context.path(file), checker)
    else:
        factory = ImageResourceFactory(_context.path(image), checker)

    _context.action(
        discriminator = ('resource', name, IBrowserPresentation, layer),
        callable = handler,
        args = (Resources, 'provideResource',
                name, IBrowserPresentation, factory, layer),
        )
