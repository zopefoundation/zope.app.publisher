##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Provide zope app-server customizatioin of publisher browser facilities

$Id$
"""

from zope.interface import implements
from zope.publisher.browser import BrowserLanguages
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import IModifiableUserPreferredLanguages

from zope.publisher.defaultview import IDefaultViewNameAPI #BBB import
from zope.publisher.defaultview import getDefaultViewName #BBB import
from zope.publisher.defaultview import queryDefaultViewName #BBB import


class NotCompatibleAdapterError(Exception):
    """Adapter not compatible with
       zope.i18n.interfaces.IModifiableBrowserLanguages has been used.
    """

key = "zope.app.publisher.browser.IUserPreferredLanguages"

class CacheableBrowserLanguages(BrowserLanguages):

    implements(IUserPreferredLanguages)

    def getPreferredLanguages(self):
        languages_data = self._getLanguagesData()
        if "overridden" in languages_data:
            return languages_data["overridden"]
        elif "cached" not in languages_data:
            languages_data["cached"] = super(
                CacheableBrowserLanguages, self).getPreferredLanguages()
        return languages_data["cached"]

    def _getLanguagesData(self):
        annotations = self.request.annotations
        languages_data = annotations.get(key)
        if languages_data is None:
            annotations[key] = languages_data = {}
        return languages_data

class ModifiableBrowserLanguages(CacheableBrowserLanguages):

    implements(IModifiableUserPreferredLanguages)

    def setPreferredLanguages(self, languages):
        languages_data = self.request.annotations.get(key)
        if languages_data is None:
            # Better way to create a compatible with
            # IModifiableUserPreferredLanguages adapter is to use
            # CacheableBrowserLanguages as base class or as example.
            raise NotCompatibleAdapterError("Adapter not compatible with "
                "zope.i18n.interfaces.IModifiableBrowserLanguages "
                "has been used.")
        languages_data["overridden"] = languages
        self.request.setupLocale()
