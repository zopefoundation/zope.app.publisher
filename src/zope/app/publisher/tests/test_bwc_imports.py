#############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

import importlib
import unittest


def _make_import_test(mod_name, attrname):
    def test(self):
        mod = importlib.import_module('zope.app.publisher.' + mod_name)
        self.assertIsNotNone(getattr(mod, attrname, None),
                             str(mod) + ' has no ' + attrname)

    return test


class TestBWCImports(unittest.TestCase):

    for mod_name, attrname in (
            ('fileresource', 'Image'),
            ('i18n', 'ZopeMessageFactory'),
            ('interfaces.ftp', 'IFTPDirectoryPublisher'),
            ('interfaces.http', 'ILogin'),
            ('pagetemplateresource', 'PageTemplate'),
            ('browser.directoryresource', 'DirectoryResourceFactory'),
            ('browser.fields', 'MenuField'),
            ('browser.fileresource', 'ImageResourceFactory'),
            ('browser.i18nfileresource', 'I18nFileResource'),
            ('browser.i18nresourcemeta', 'I18nResource'),
            ('browser.icon', 'IconView'),
            ('browser.menu', 'BrowserMenu'),
            ('browser.menumeta', 'menuDirective'),
            ('browser.metaconfigure', 'defaultView'),
            ('browser.metadirectives', 'IIconDirective'),
            ('browser.pagetemplateresource', 'PageTemplateResource'),
            ('browser.resource', 'AbsoluteURL'),
            ('browser.resourcemeta', 'resource'),
            ('browser.resources', 'Resources'),
            ('browser.viewmeta', 'page'),
            ('browser.menumeta', 'menuDirective')):
        locals()['test_' + mod_name] = _make_import_test(mod_name, attrname)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
