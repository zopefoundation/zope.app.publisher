##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Provide zope app-server customizatioin of publisher browser facilities

$Id: __init__.py,v 1.4 2003/10/29 20:25:27 sidnei Exp $
"""

import zope.publisher.browser
import zope.app.location

class BrowserView(zope.publisher.browser.BrowserView,
                  zope.app.location.Location,
                  ):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context


