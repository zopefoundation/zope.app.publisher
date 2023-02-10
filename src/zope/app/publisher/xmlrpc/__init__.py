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
"""XML-RPC Publisher Components

This module contains the XMLRPCView.
"""

import zope.interface
import zope.location
import zope.publisher.interfaces.xmlrpc
from zope.publisher.xmlrpc import XMLRPCView

import zope.app.publisher.interfaces.xmlrpc


class IMethodPublisher(zope.interface.Interface):
    """Marker interface for an object that wants to publish methods
    """

# Need to test new __parent__ attribute


@zope.interface.implementer(IMethodPublisher)
class MethodPublisher(XMLRPCView, zope.location.Location):
    """Base class for very simple XML-RPC views that publish methods

    This class is meant to be more of an example than a standard base class.

    This example is explained in the README.txt file for this package
    """

    @property
    def __parent__(self):
        return hasattr(self, '_parent') and self._parent or self.context

    @__parent__.setter
    def __parent__(self, parent):
        self._parent = parent


@zope.interface.implementer(
    zope.publisher.interfaces.xmlrpc.IXMLRPCPublisher)
class MethodTraverser:

    __used_for__ = IMethodPublisher

    def __init__(self, context, request):
        self.context = context

    def publishTraverse(self, request, name):
        return getattr(self.context, name)
