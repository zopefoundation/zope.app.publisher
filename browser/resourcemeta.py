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
import os

from zope.app import zapi
from zope.security.checker import CheckerPublic, NamesChecker
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.component.metaconfigure import handler

from fileresource import FileResourceFactory, ImageResourceFactory
from pagetemplateresource import PageTemplateResourceFactory
from directoryresource import DirectoryResourceFactory

allowed_names = ('GET', 'HEAD', 'publishTraverse', 'browserDefault',
                 'request', '__call__')

def resource(_context, name, layer='default', permission='zope.Public',
             file=None, image=None, template=None):

    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names, permission)

    if ((file and image) or (file and template) or
        (image and template) or not (file or image or template)):
        raise ConfigurationError(
            "Must use exactly one of file or image or template"
            " attributes for resource directives"
            )

    if file:
        factory = FileResourceFactory(file, checker, name)
    elif image:
        factory = ImageResourceFactory(image, checker, name)
    else:
        factory = PageTemplateResourceFactory(template, checker, name)

    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = (zapi.servicenames.Presentation, 'provideResource',
                name, IBrowserRequest, factory, layer),
        )

def resourceDirectory(_context, name, directory, layer='default',
                      permission='zope.Public'):
    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names + ('__getitem__', 'get'),
                           permission)

    if not os.path.isdir(directory):
        raise ConfigurationError(
            "Directory %s does not exist" % directory
            )

    factory = DirectoryResourceFactory(directory, checker, name)
    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = (zapi.servicenames.Presentation, 'provideResource',
                name, IBrowserRequest, factory, layer),
        )
