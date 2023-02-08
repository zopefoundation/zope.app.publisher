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
"""'xmlrpc' ZCML Namespace Schemas

$Id$
"""
import zope.configuration.fields
import zope.interface
import zope.schema
import zope.security.zcml


class IViewDirective(zope.interface.Interface):
    """View Directive for XML-RPC methods."""

    for_ = zope.configuration.fields.GlobalObject(
        title="Published Object Type",
        description="""The types of objects to be published via XML-RPC

        This can be expressed with either a class or an interface
        """,
        required=True,
    )

    interface = zope.configuration.fields.Tokens(
        title="Interface to be published.",
        required=False,
        value_type=zope.configuration.fields.GlobalInterface()
    )

    methods = zope.configuration.fields.Tokens(
        title="Methods (or attributes) to be published",
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier()
    )

    class_ = zope.configuration.fields.GlobalObject(
        title="Class",
        description="A class that provides attributes used by the view.",
        required=False
    )

    permission = zope.security.zcml.Permission(
        title="Permission",
        description="""The permission needed to use the view.

        If this option is used and a name is given for the view, then
        the names defined by the given methods or interfaces will be
        under the given permission.

        If a name is not given for the view, then, this option is required and
        the given permission is required to call the individual views defined
        by the given interface and methods.

        (See the name attribute.)

        If no permission is given, then permissions should be declared
        for the view using other means, such as the class directive.
        """,
        required=False)

    name = zope.schema.TextLine(
        title="The name of the view.",
        description="""

        If a name is given, then rpc methods are accessed by
        traversing the name and then accessing the methods.  In this
        case, the class should implement
        zope.pubisher.interfaces.IPublishTraverse.

        If no name is provided, then the names given by the attributes
        and interfaces are published directly as callable views.

        """,
        required=False,
    )
