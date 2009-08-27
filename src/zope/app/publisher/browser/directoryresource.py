##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Resource Directory

A 'resource directory' is an on-disk directory which is registered as
a resource using the <resourceDirectory> ZCML directive.  The
directory is treated as a source for individual resources; it can be
traversed to retrieve resources represented by contained files, which
can in turn be treated as resources.  The contained files have
__name__ values which include a '/' separating the __name__ of the
resource directory from the name of the file within the directory.

$Id$
"""
# BBB imports
from zope.browserresource.directory import Directory, DirectoryResource
from zope.browserresource.directory import DirectoryResourceFactory
