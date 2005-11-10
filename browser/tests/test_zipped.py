##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Test harness for loading pages from packages contained in ZIP archives.

"""
__docformat__ = "reStructuredText"

import os
import sys

from zope.app.testing import functional


#### test setup ####

class Layer(functional.ZCMLLayer):

    # This layer still can't be completely torn down due to the base
    # class, but tries to avoid doing more damage than it has to.

    def setUp(self):
        self.__sys_path = sys.path[:]
        here = os.path.dirname(__file__)
        zipfile = os.path.join(here, "testfiles", "zippedview.zip")
        sys.path.append(zipfile)
        functional.ZCMLLayer.setUp(self)

    def tearDown(self):
        sys.path[:] = self.__sys_path
        functional.ZCMLLayer.tearDown(self)


ZippedViewLayer = Layer(
    os.path.join(os.path.dirname(__file__), "testfiles/zippedview.zcml"),
    __name__, "ZippedViewLayer")

def test_suite():
    suite = functional.FunctionalDocFileSuite("zipped.txt")
    suite.layer = ZippedViewLayer
    return suite
