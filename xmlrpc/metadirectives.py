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
"""'xmlrpc' ZCML Namespace Schemas

$Id$
"""
from zope.app.component.metadirectives import IBasicViewInformation
from zope.configuration.fields import GlobalObject
from zope.interface import Interface
from zope.schema import TextLine

class IViewDirective(IBasicViewInformation):
    """View Directive for XML-RPC methods."""

    name = TextLine(
        title=u"The name of the view.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=False)


class IDefaultViewDirective(Interface):
    """
    The name of the view that should be the default.
              
    This name refers to view that should be the
    view used by default (if no view name is supplied
    explicitly).
    """

    name = TextLine(
        title=u"The name of the view that should be the default.",
        description=u"""
        This name refers to view that should be the view used by
        default (if no view name is supplied explicitly).""",
        required=True
        )

    for_ = GlobalObject(
        title=u"The interface this view is the default for.",
        description=u"""Specifies the interface for which the view is
        registered. All objects implementing this interface can make use of
        this view. If this attribute is not specified, the view is available
        for all objects.""",
        required=False
        )
