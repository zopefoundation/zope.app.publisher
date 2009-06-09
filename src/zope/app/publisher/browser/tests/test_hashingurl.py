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
"""Test for hashed resource-URLs

$Id: test_directoryresource.py 95447 2009-01-29 16:28:18Z wosc $
"""
import os
import re
import tempfile
import unittest
import zope.app.publisher.browser.directoryresource
import zope.app.publisher.browser.tests
import zope.app.publisher.testing
import zope.app.testing.functional
import zope.app.testing.placelesssetup
import zope.publisher.browser
import zope.security.checker
import zope.site.hooks
import zope.testbrowser.testing

fixture = os.path.join(
    os.path.dirname(zope.app.publisher.browser.tests.__file__), 'testfiles')

checker = zope.security.checker.NamesChecker(
    ('get', '__getitem__', 'request', 'publishTraverse')
    )

HashedResourcesLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'hashedresources.zcml'),
    __name__, 'HashedResourcesLayer', allow_teardown=True)


class HashingURLTest(zope.app.testing.functional.FunctionalTestCase):

    layer = HashedResourcesLayer

    def assertMatches(self, regex, text):
        self.assert_(re.match(regex, text), "/%s/ did not match '%s'" % (
            regex, text))

    def setUp(self):
        super(HashingURLTest, self).setUp()
        self.site = zope.site.hooks.getSite()

        self.tmpdir = tempfile.mkdtemp()
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('')
        self.dirname = os.path.basename(self.tmpdir)

        self.request = zope.publisher.browser.TestRequest()
        self.request._vh_root = self.site
        self.directory = zope.app.publisher.browser.directoryresource.DirectoryResourceFactory(
            self.tmpdir, checker, self.dirname)(self.request)
        self.directory.__parent__ = self.site

    def _hash(self, text):
        return re.match('http://127.0.0.1/\+\+noop\+\+([^/]*)/.*', text).group(1)

    def test_directory_url_should_contain_hash(self):
        self.assertMatches(
            'http://127.0.0.1/\+\+noop\+\+[^/]*/@@/%s' % self.dirname, self.directory())

    def test_file_url_should_contain_hash(self):
        file = zope.app.publisher.browser.fileresource.FileResourceFactory(
            os.path.join(fixture, 'test.txt'), checker, 'test.txt')(self.request)
        self.assertMatches(
            'http://127.0.0.1/\+\+noop\+\+[^/]*/@@/test.txt', file())

    def test_different_files_hashes_should_differ(self):
        file1 = zope.app.publisher.browser.fileresource.FileResourceFactory(
            os.path.join(fixture, 'test.txt'), checker, 'test.txt')(self.request)
        file2 = zope.app.publisher.browser.fileresource.FileResourceFactory(
            os.path.join(fixture, 'test.pt'), checker, 'test.txt')(self.request)
        self.assertNotEqual(self._hash(file1()), self._hash(file2()))

    def test_directory_contents_changed_hash_should_change(self):
        before = self._hash(self.directory())
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('foo')
        after = self._hash(self.directory())
        self.assertNotEqual(before, after)


class DeveloperModeTest(HashingURLTest):

    def test_production_mode_hash_should_not_change(self):
        zope.component.provideAdapter(
            zope.app.publisher.browser.resource.CachingContentsHash,
            (zope.app.publisher.browser.directoryresource.DirectoryResource,))

        before = self._hash(self.directory())
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('foo')
        after = self._hash(self.directory())
        self.assertEqual(before, after)


class BrowserTest(zope.app.testing.functional.FunctionalTestCase):

    layer = HashedResourcesLayer

    def setUp(self):
        super(BrowserTest, self).setUp()
        self.browser = zope.testbrowser.testing.Browser()
        self.directory = zope.component.getAdapter(
            zope.publisher.browser.TestRequest(), name='myresource')

    def test_traverse_atat_by_name(self):
        self.browser.open('http://localhost/@@/myresource/test.txt')
        self.assertEqual('test\ndata\n', self.browser.contents)

    def test_traverse_atat_by_hash(self):
        hash = str(
            zope.app.publisher.interfaces.IResourceContentsHash(self.directory))
        self.browser.open(
            'http://localhost/++noop++%s/@@/myresource/test.txt' % hash)
        self.assertEqual('test\ndata\n', self.browser.contents)

    def test_traverse_resource_by_name(self):
        self.browser.open('http://localhost/++resource++myresource/test.txt')
        self.assertEqual('test\ndata\n', self.browser.contents)

    def test_traverse_resource_by_hash(self):
        hash = str(
            zope.app.publisher.interfaces.IResourceContentsHash(self.directory))
        self.browser.open(
            'http://localhost/++noop++%s/++resource++myresource/test.txt' % hash)
        self.assertEqual('test\ndata\n', self.browser.contents)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HashingURLTest))
    suite.addTest(unittest.makeSuite(DeveloperModeTest))
    suite.addTest(unittest.makeSuite(BrowserTest))
    return suite
