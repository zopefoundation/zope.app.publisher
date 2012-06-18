##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Test that menu items are re-registered in subsequent layers.

Menu items registered with <browser:page/> were not re-registered after the
first functional test layer ran. In any subsequent functional test layer the
items where not availabe (introduced in 3.5.0a3)

"""

import os.path
import unittest
import zope.app.testing.functional
import zope.publisher.browser
import zope.publisher.interfaces.browser


layer1 = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'menutestlayer.zcml'),
    __name__, 'MenuTestLayer1', allow_teardown=True)
layer2 = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'menutestlayer.zcml'),
    __name__, 'MenuTestLayer2', allow_teardown=True)


class View(object):
    pass


class TestLayerMenuReuse1(zope.app.testing.functional.BrowserTestCase):

    layer = layer1

    def test_menu(self):
        request = zope.publisher.browser.TestRequest()
        item = zope.app.publisher.browser.menu.getFirstMenuItem(
            'test_menu', object(), request)
        self.assertNotEqual(None, item)

class TestLayerMenuReuse2(TestLayerMenuReuse1):

    layer = layer2


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLayerMenuReuse1))
    suite.addTest(unittest.makeSuite(TestLayerMenuReuse2))
    return suite

