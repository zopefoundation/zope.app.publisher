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
"""XML-RPC Publisher Components

This module contains the MethodPublisher, and XMLRPCView.

$Id$
"""
from zope.interface import implements
from zope.app.publisher.interfaces.xmlrpc import IXMLRPCView

class XMLRPCView(object):
    """A base XML-RPC view that can be used as mix-in for XML-RPC views.""" 

    implements(IXMLRPCView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
