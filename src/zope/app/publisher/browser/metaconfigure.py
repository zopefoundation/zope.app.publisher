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
"""Browser configuration code"""
from zope.browserpage.metaconfigure import view
# BBB imports
from zope.browserresource.metaconfigure import I18nResource
from zope.browserresource.metaconfigure import resource
from zope.browserresource.metaconfigure import resourceDirectory
from zope.publisher.zcml import defaultSkin
from zope.publisher.zcml import defaultView
from zope.publisher.zcml import setDefaultSkin
