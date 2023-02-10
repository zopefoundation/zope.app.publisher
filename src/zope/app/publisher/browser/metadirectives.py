#############################################################################
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

This module defines the schemas for browser directives.
"""
from zope.browsermenu.metadirectives import IAddMenuItemDirective
from zope.browsermenu.metadirectives import IMenuDirective
from zope.browsermenu.metadirectives import IMenuItem
from zope.browsermenu.metadirectives import IMenuItemDirective
from zope.browsermenu.metadirectives import IMenuItemsDirective
from zope.browsermenu.metadirectives import IMenuItemSubdirective
from zope.browsermenu.metadirectives import ISubMenuItemDirective
from zope.browsermenu.metadirectives import ISubMenuItemSubdirective
from zope.browserpage.metadirectives import IPageDirective
from zope.browserpage.metadirectives import IPagesDirective
from zope.browserpage.metadirectives import IPagesPageSubdirective
from zope.browserpage.metadirectives import IViewDefaultPageSubdirective
from zope.browserpage.metadirectives import IViewDirective
from zope.browserpage.metadirectives import IViewPageSubdirective
# BBB imports
from zope.browserresource.metadirectives import IBasicResourceInformation
from zope.browserresource.metadirectives import II18nResourceDirective
from zope.browserresource.metadirectives import \
    II18nResourceTranslationSubdirective
from zope.browserresource.metadirectives import IIconDirective
from zope.browserresource.metadirectives import IResourceDirective
from zope.browserresource.metadirectives import IResourceDirectoryDirective
from zope.publisher.zcml import IDefaultSkinDirective
from zope.publisher.zcml import IDefaultViewDirective
