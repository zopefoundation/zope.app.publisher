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
   'BrowserAdd__zope.app.publisher.browser.tests.test_addMenuItem.X'),
  <function handler>,
  ('Utilities',
   'provideUtility',
   <InterfaceClass zope.component.interfaces.IFactory>,
   <zope.component.factory.Factory object>,
   'BrowserAdd__zope.app.publisher.browser.tests.test_addMenuItem.X')),
 (None,
  <function provideInterface>,
  ('zope.component.interfaces.IFactory',
   <InterfaceClass zope.component.interfaces.IFactory>)),
 (None,
  <function handler>,
  ('Adapters',
   'subscribe',
   (<InterfaceClass zope.app.container.interfaces.IAdding>,
    <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
   <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>,
   <function MenuItemFactory>)),
 (None,
  <function provideInterface>,
  ('',
   <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>)),
 (None,
  <function provideInterface>,
  ('',
   <InterfaceClass zope.app.container.interfaces.IAdding>)),
 (None,
  <function provideInterface>,
  ('',
   <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>)))

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
    ((None,
      <function handler>,
      ('Adapters',
       'subscribe',
       (<InterfaceClass zope.app.container.interfaces.IAdding>,
        <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
       <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>,
       <function MenuItemFactory>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.container.interfaces.IAdding>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>)))
    """

def test_w_factory_and_view():
    """
    >>> context = Context()
    >>> addMenuItem(context, factory="x.y.z", title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo", view="AddX")
    >>> context
    ((None,
      <function handler>,
      ('Adapters',
       'subscribe',
       (<InterfaceClass zope.app.container.interfaces.IAdding>,
        <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
       <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>,
       <function MenuItemFactory>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.container.interfaces.IAdding>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>)))
    """

def test_w_factory_class_view():
    """
    >>> context = Context()
    >>> addMenuItem(context, class_=X, title="Add an X",
    ...             permission="zope.ManageContent", description="blah blah",
    ...             filter="context/foo", view="AddX")
    >>> import pprint
    >>> context
    ((('utility',
       <InterfaceClass zope.component.interfaces.IFactory>,
       'BrowserAdd__zope.app.publisher.browser.tests.test_addMenuItem.X'),
      <function handler>,
      ('Utilities',
       'provideUtility',
       <InterfaceClass zope.component.interfaces.IFactory>,
       <zope.component.factory.Factory object>,
       'BrowserAdd__zope.app.publisher.browser.tests.test_addMenuItem.X')),
     (None,
      <function provideInterface>,
      ('zope.component.interfaces.IFactory',
       <InterfaceClass zope.component.interfaces.IFactory>)),
     (None,
      <function handler>,
      ('Adapters',
       'subscribe',
       (<InterfaceClass zope.app.container.interfaces.IAdding>,
        <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
       <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>,
       <function MenuItemFactory>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.publisher.interfaces.browser.AddMenu>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.container.interfaces.IAdding>)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>)))
"""


def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__': unittest.main()
