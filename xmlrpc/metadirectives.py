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
"""'xmlrpc' ZCML Namespace Schemas

$Id: metadirectives.py,v 1.1 2003/08/03 23:47:47 srichter Exp $
"""
from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, PythonIdentifier
from zope.schema import TextLine, Id

class IViewDirective(Interface):
    """View Directive for XML-RPC methods."""

    name = TextLine(
        title=u"The name of the view.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=False)

    factory = Tokens(
        title=u"Factory",
        description=u"Specifies a component that is used to provide the "\
                    u"methods.",
        value_type=GlobalObject(),
        required=False)

    for_ = GlobalObject(
        title=u"The interface this view applies to.",
        description=u"""
        The view will be for all objects that implement this
        interface. If this is not supplied, the view applies to all
        objects.""",
        required=False)

    permission = Id(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False)

    allowed_interface = Tokens(
        title=u"Interface that is also allowed if user has permission.",
        description=u"""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying this attribute, you can
        make the permission also apply to everything described in the
        supplied interface.

        Multiple interfaces can be provided, separated by
        whitespace.""",
        required=False,
        value_type=GlobalObject() )

    allowed_methods = Tokens(
        title=u"View attributes that are also allowed if user has permission.",
        description=u"""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying 'allowed_methods',
        you can make the permission also apply to the extra attributes
        on the view object.""",
        required=False,
        value_type=PythonIdentifier() )


class IMethodDirective(Interface):
    """This is the method subdirective."""

    name = TextLine(
        title=u"The name of the view.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=True)

    permission = Id(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False)

    attribute = PythonIdentifier(
        title=u"Attribute",
        description=u"The attribute that describes the method that will be "\
                    u"known as 'name'",
        required=False)
