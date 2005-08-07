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
"""Test Modifiable Browser Languages detector

$Id$
"""
import unittest

from zope.interface import directlyProvides
from zope.publisher.tests.test_browserlanguages import BrowserLanguagesTest
from zope.publisher.tests.test_browserlanguages import TestRequest

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.annotation import IAttributeAnnotatable, IAnnotations
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.publisher.browser import ModifiableBrowserLanguages


class ModifiableBrowserLanguagesTests(PlacelessSetup, BrowserLanguagesTest):

    def setUp(self):
        super(ModifiableBrowserLanguagesTests, self).setUp()
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)

    def factory(self, request):
        directlyProvides(request, IAttributeAnnotatable)
        return ModifiableBrowserLanguages(request)

    def test_setPreferredLanguages(self):
        browser_languages = self.factory(TestRequest("da, en, pt"))
        self.assertEqual(list(browser_languages.getPreferredLanguages()),
            ["da", "en", "pt"])
        browser_languages.setPreferredLanguages(["ru", "en"])
        self.assertEqual(list(browser_languages.getPreferredLanguages()),
            ["ru", "en"])

    def test_cached_languages(self):
        request = TestRequest("da, en, pt")
        browser_languages = self.factory(request)
        self.assertEqual(list(browser_languages.getPreferredLanguages()),
            ["da", "en", "pt"])
        request["HTTP_ACCEPT_LANGUAGE"] = "ru, en"
        self.assertEqual(list(browser_languages.getPreferredLanguages()),
            ["da", "en", "pt"])


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(ModifiableBrowserLanguagesTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
