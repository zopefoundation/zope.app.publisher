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
"""Browser Resource

$Id$
"""
from zope.app.publisher.interfaces import IResource, IResourceContentsHash
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implements, implementsOnly, Interface
from zope.location import Location
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.site.hooks import getSite
from zope.traversing.interfaces import ITraversable
from zope.traversing.browser.interfaces import IAbsoluteURL
import os
import md5
import zope.traversing.browser.absoluteurl


class Resource(Location):

    implements(IResource)

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return str(getMultiAdapter((self, self.request), IAbsoluteURL))


class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    implementsOnly(IAbsoluteURL)
    adapts(IResource, IDefaultBrowserLayer)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.name = self.context.__name__
        if self.name.startswith('++resource++'):
            self.name = self.name[12:]

    def _site_url(self):
        site = getSite()
        base = queryMultiAdapter((site, self.request), IAbsoluteURL,
            name="resource")
        if base is None:
            url = str(getMultiAdapter((site, self.request), IAbsoluteURL))
        else:
            url = str(base)
        return url

    def __str__(self):
        return "%s/@@/%s" % (self._site_url(), self.name)


class HashingURL(AbsoluteURL):
    """Inserts a hash of the contents into the resource's URL,
    so the URL changes whenever the contents change, thereby forcing
    a browser to update its cache.
    """

    def __str__(self):
        hash = str(IResourceContentsHash(self.context))
        return "%s/++noop++%s/@@/%s" % (self._site_url(), hash, self.name)


class ContentsHash(object):

    implements(zope.app.publisher.interfaces.IResourceContentsHash)

    def __init__(self, context):
        self.context = context

    def __str__(self):
        path = self.context.context.path
        if os.path.isdir(path):
            files = self._list_directory(path)
        else:
            files = [path]

        result = md5.new()
        for file in files:
            f = open(file, 'rb')
            data = f.read()
            f.close()
            result.update(data)
        result = result.hexdigest()
        return result

    def _list_directory(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                yield os.path.join(root, file)


_contents_hash = {}

class CachingContentsHash(ContentsHash):

    def __str__(self):
        path = self.context.context.path
        try:
            return _contents_hash[path]
        except KeyError:
            result = super(CachingContentsHash, self).__str__()
            _contents_hash[path] = result
            return result


class NoOpTraverser(object):
    """This traverser simply skips a path element,
    so /foo/++noop++qux/bar is equivalent to /foo/bar.

    This is useful to generate varying URLs to work around browser caches.
    """

    adapts(Interface, IDefaultBrowserLayer)
    implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        return self.context
