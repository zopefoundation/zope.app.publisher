#############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test the addMenuItem directive

>>> context = Context()
>>> addMenuItem(context, class_=X, title="Add an X",
...             permission="zope.ManageContent")
>>> context
((('utility',
   <InterfaceClass zope.component.interfaces.IFactory>,
   'zope.app.browser.add.zope.app.publisher.browser.tests.test_addMenuItem.X'),
  <function handler>,
  ('Utilities',
   'provideUtility',
   <InterfaceClass zope.component.interfaces.IFactory>,
   <zope.component.factory.Factory object>,
   'zope.app.browser.add.""" \
         """zope.app.publisher.browser.tests.test_addMenuItem.X')),
 (None,
  <function provideInterface>,
  ('zope.component.interfaces.IFactory',
   <InterfaceClass zope.component.interfaces.IFactory>)),
 (('browser:menuItem',
   'zope.app.container.add',
   <InterfaceClass zope.app.container.interfaces.IAdding>,
   'Add an X'),
  <bound method GlobalBrowserMenuService.menuItem of """ \
     """<zope.app.publisher.browser.globalbrowsermenuservice.""" \
     """GlobalBrowserMenuService object>>,
  ('zope.app.container.add',
   <InterfaceClass zope.app.container.interfaces.IAdding>,
   'zope.app.browser.add.zope.app.publisher.browser.tests.test_addMenuItem.X',
   'Add an X',
   '',
   None,
   'zope.ManageContent',
   {'factory': 'zope.app.browser.add.""" \
         """zope.app.publisher.browser.tests.test_addMenuItem.X'})))

$Id$
"""

import unittest
from zope.testing.doctestunit import DocTestSuite
import re
import pprint
import cStringIO
from zope.app.publisher.browser.metaconfigure import addMenuItem

atre = re.compile(' at [0-9a-fA-Fx]+')

class X(object):
    pass

class Context(object):
    actions = ()
    
    def action(self, discriminator, callable, args):
        self.actions += ((discriminator, callable, args), )

    def __repr__(self):
        stream = cStringIO.StringIO()
        pprinter = pprint.PrettyPrinter(stream=stream, width=60)
        pprinter.pprint(self.actions)
        r = stream.getvalue()
        return (''.join(atre.split(r))).strip()


def test_w_factory():
    """
    >>> context = Context()
    >>> addMenuItem(context, factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo")
    >>> context
    ((('browser:menuItem',
       'zope.app.container.add',
       <InterfaceClass zope.app.container.interfaces.IAdding>,
       'Add an X'),
      <bound method GlobalBrowserMenuService.menuItem of """ \
            """<zope.app.publisher.browser.globalbrowsermenuservice.""" \
            """GlobalBrowserMenuService object>>,
      ('zope.app.container.add',
       <InterfaceClass zope.app.container.interfaces.IAdding>,
       'x.y.z',
       'Add an X',
       'blah blah',
       'context/foo',
       'zope.ManageContent',
       {'factory': 'x.y.z'})),)
    """

def test_w_factory_and_view():
    """
    >>> context = Context()
    >>> addMenuItem(context, factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo", view="AddX")
    >>> context
    ((('browser:menuItem',
       'zope.app.container.add',
       <InterfaceClass zope.app.container.interfaces.IAdding>,
       'Add an X'),
      <bound method GlobalBrowserMenuService.menuItem of """ \
            """<zope.app.publisher.browser.globalbrowsermenuservice.""" \
            """GlobalBrowserMenuService object>>,
      ('zope.app.container.add',
       <InterfaceClass zope.app.container.interfaces.IAdding>,
       'AddX',
       'Add an X',
       'blah blah',
       'context/foo',
       'zope.ManageContent',
       {'factory': 'x.y.z'})),)
    """

def test_w_factory_class_view():
    """
    >>> context = Context()
    >>> addMenuItem(context, class_=X, title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo", view="AddX")
    >>> context
    ((('utility',
       <InterfaceClass zope.component.interfaces.IFactory>,
       'zope.app.browser.add.""" \
         """zope.app.publisher.browser.tests.test_addMenuItem.X'),
      <function handler>,
      ('Utilities',
       'provideUtility',
       <InterfaceClass zope.component.interfaces.IFactory>,
       <zope.component.factory.Factory object>,
       'zope.app.browser.add.""" \
         """zope.app.publisher.browser.tests.test_addMenuItem.X')),
     (None,
      <function provideInterface>,
      ('zope.component.interfaces.IFactory',
       <InterfaceClass zope.component.interfaces.IFactory>)),
     (('browser:menuItem',
       'zope.app.container.add',
       <InterfaceClass zope.app.container.interfaces.IAdding>,
       'Add an X'),
      <bound method GlobalBrowserMenuService.menuItem of """ \
         """<zope.app.publisher.browser.globalbrowsermenuservice.""" \
         """GlobalBrowserMenuService object>>,
      ('zope.app.container.add',
       <InterfaceClass zope.app.container.interfaces.IAdding>,
       'AddX',
       'Add an X',
       'blah blah',
       'context/foo',
       'zope.ManageContent',
       {'factory': 'zope.app.browser.add.""" \
         """zope.app.publisher.browser.tests.test_addMenuItem.X'})))
"""


def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__': unittest.main()
