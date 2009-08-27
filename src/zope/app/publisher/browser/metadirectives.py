#############################################################################
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

This module defines the schemas for browser directives.

$Id$
"""
# BBB imports
from zope.browserresource.metadirectives import (
    IBasicResourceInformation,
    IResourceDirective,
    II18nResourceDirective,
    II18nResourceTranslationSubdirective,
    IResourceDirectoryDirective,
    IIconDirective
)
from zope.browsermenu.metadirectives import (
    IMenuDirective,
    IMenuItemsDirective,
    IMenuItem,
    IMenuItemSubdirective,
    IMenuItemDirective,
    ISubMenuItemSubdirective,
    ISubMenuItemDirective,
    IAddMenuItemDirective,
)
from zope.browserpage.metadirectives import (
    IPagesDirective,
    IViewDirective,
    IViewPageSubdirective,
    IViewDefaultPageSubdirective,
    IPagesPageSubdirective,
    IPageDirective,
)
from zope.publisher.zcml import IDefaultSkinDirective, IDefaultViewDirective
