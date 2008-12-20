##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
from zope.component.interfaces import ComponentLookupError, IDefaultViewName
from zope.component import getSiteManager

import zope.interface
from zope.interface import implements
from zope.publisher.browser import BrowserLanguages
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import IModifiableUserPreferredLanguages

##############################################################################
# BBB 2006/04/03 - to be removed after 12 months

import zope.deferredimport
zope.deferredimport.deprecated(
    "It has been moved to zope.publisher.browser. This reference will "
    "be removed in Zope 3.5.",
    BrowserView = 'zope.publisher.browser:BrowserView',
    applySkin = 'zope.publisher.browser:applySkin',
    )

#
##############################################################################

class IDefaultViewNameAPI(zope.interface.Interface):

    def getDefaultViewName(object, request, context=None):
        """Get the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides the
        desired view type.  The nearest one to the object is found.
        If a matching default view name cannot be found, raises
        ComponentLookupError.

        If context is not specified, attempts to use
        object to specify a context.
        """

    def queryDefaultViewName(object, request, default=None, context=None):
        """Look for the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides
        the desired view type.  The nearest one to the object is
        found.  If a matching default view name cannot be found,
        returns the default.

        If context is not specified, attempts to use object to specify
        a context.
        """

# TODO: needs tests
def getDefaultViewName(object, request, context=None):
    name = queryDefaultViewName(object, request, context=context)
    if name is not None:
        return name
    raise ComponentLookupError("Couldn't find default view name",
                               context, request)

def queryDefaultViewName(object, request, default=None, context=None):
    """
    query the default view for a given object and request.

      >>> from zope.app.publisher.browser import queryDefaultViewName

    lets create an object with a default view.

      >>> import zope.interface
      >>> class IMyObject(zope.interface.Interface):
      ...   pass
      >>> class MyObject(object):
      ...   zope.interface.implements(IMyObject)
      >>> queryDefaultViewName(MyObject(), object()) is None
      True

    Now we can will set a default view.

      >>> import zope.component
      >>> import zope.component.interfaces
      >>> zope.component.provideAdapter('name',
      ...     adapts=(IMyObject, zope.interface.Interface),
      ...     provides=zope.component.interfaces.IDefaultViewName)
      >>> queryDefaultViewName(MyObject(), object())
      'name'

    This also works if the name is empty

      >>> zope.component.provideAdapter('',
      ...     adapts=(IMyObject, zope.interface.Interface),
      ...     provides=zope.component.interfaces.IDefaultViewName)
      >>> queryDefaultViewName(MyObject(), object())
      ''
    """
    name = getSiteManager(context).adapters.lookup(
        map(zope.interface.providedBy, (object, request)), IDefaultViewName)
    if name is None:
        return default
    return name

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
