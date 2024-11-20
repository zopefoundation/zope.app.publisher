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
"""Test of field converters.

"""
import unittest
from datetime import datetime

from zope.app.publisher.fieldconverters import field2date_via_datetimeutils
from zope.app.publisher.fieldconverters import registerZopeConverters


class TestFieldConverters(unittest.TestCase):

    def test_field2date_dateonly(self, value="2003/05/04"):
        dt = field2date_via_datetimeutils(value)
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2003)
        self.assertEqual(dt.month, 5)
        self.assertEqual(dt.day, 4)
        self.assertEqual(dt.hour, 0)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)
        self.assertEqual(dt.tzinfo, None)

    def test_field2date_reads(self):
        from io import StringIO
        sio = StringIO('2003/05/04')
        self.test_field2date_dateonly(sio)

    def test_field2date_timestamp(self):
        dt = field2date_via_datetimeutils('2003/05/04 19:26:54')
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2003)
        self.assertEqual(dt.month, 5)
        self.assertEqual(dt.day, 4)
        self.assertEqual(dt.hour, 19)
        self.assertEqual(dt.minute, 26)
        self.assertEqual(dt.second, 54)
        self.assertEqual(dt.tzinfo, None)

    def test_register(self):
        registerZopeConverters()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
