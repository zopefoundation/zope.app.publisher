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
"""Browser Menu Directives Tests

$Id$
"""

from StringIO import StringIO
from unittest import TestCase, main, makeSuite

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.publisher.browser import TestRequest
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.publisher.browser.globalbrowsermenuservice \
    import globalBrowserMenuService

import zope.app.publisher.browser

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.publisher.browser)()

    def test(self):
        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_id" title="test menu" />

            <browser:menuItems menu="test_id" for="zope.interface.Interface">
              <browser:menuItem action="a1" title="t1" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           zope.app.publisher.browser.tests.test_globalbrowsermenuservice.I1
              ">
              <browser:menuItem action="a2" title="t2" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           zope.app.publisher.browser.tests.test_globalbrowsermenuservice.I11
              ">
              <browser:menuItem action="a3" title="t3" filter="context" />
              <browser:menuItem action="a4" title="t4" filter="not:context" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           zope.app.publisher.browser.tests.test_globalbrowsermenuservice.I111
              ">
              <browser:menuItem action="a5" title="t5" />
              <browser:menuItem action="a6" title="t6" />
              <browser:menuItem action="f7" title="t7" />
              <browser:menuItem action="u8" title="t8" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           zope.app.publisher.browser.tests.test_globalbrowsermenuservice.I12
              ">
              <browser:menuItem action="a9" title="t9" />
            </browser:menuItems>
            """)))


        from zope.app.publisher.browser.tests.test_globalbrowsermenuservice \
             import TestObject

        menu = globalBrowserMenuService.getMenu('test_id', TestObject(),
                                                TestRequest())

        def d(n):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "",
                    'selected': '',
                    'extra': None,
                    }

        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])

        first = globalBrowserMenuService.getFirstMenuItem(
            'test_id', TestObject(), TestRequest())

        self.assertEqual(first, d(5))


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
