##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Functional tests for xmlrpc
"""
import doctest
import re
import unittest

import zope.component
import zope.interface
import zope.publisher.interfaces.xmlrpc
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.site.interfaces import IFolder
from zope.testing import module
from zope.testing import renormalizing

from zope.app.publisher.testing import AppPublisherLayer
from zope.app.publisher.xmlrpc.testing import http


class TestMethodPublisher(unittest.TestCase):

    def test_parent(self):
        from zope.app.publisher.xmlrpc import MethodPublisher

        p = MethodPublisher(42, None)
        # Comes from the context first
        self.assertEqual(p.__parent__, 42)

        p.__parent__ = self
        self.assertEqual(p.__parent__, self)
        self.assertEqual(p._parent, self)


def setUp(test):
    module.setUp(test, 'zope.app.publisher.xmlrpc.README')


def tearDown(test):
    # clean up the views we registered:

    # we use the fact that registering None unregisters whatever is
    # registered. We can't use an unregistration call because that
    # requires the object that was registered and we don't have that handy.
    # (OK, we could get it if we want. Maybe later.)

    zope.component.provideAdapter(None, (
        IFolder,
        IXMLRPCRequest
    ), zope.interface, 'contents')

    module.tearDown(test, 'zope.app.publisher.xmlrpc.README')


def test_suite():
    checker = renormalizing.RENormalizing((
        (re.compile('<DateTime \''), '<DateTime u\''),
        (re.compile('at [-0-9a-fA-F]+'), 'at <SOME ADDRESS>'),
        (re.compile("HTTP/1.0"), "HTTP/1.1"),
    ))

    suite = doctest.DocFileSuite(
        '../README.rst',
        setUp=setUp,
        tearDown=tearDown,
        checker=checker,
        globs={'http': http},
        optionflags=(doctest.ELLIPSIS
                     | doctest.NORMALIZE_WHITESPACE)
    )
    suite.layer = AppPublisherLayer
    return unittest.TestSuite((
        suite,
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
