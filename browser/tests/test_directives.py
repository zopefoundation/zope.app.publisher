##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
import unittest
from cStringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.component.tests.views import IC, V1, VZMI, R1, RZMI
from zope.component import getView, queryView, queryResource
from zope.component import getDefaultViewName, getResource
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.proxy import ProxyFactory
from zope.proxy.introspection import removeAllProxies
import zope.configuration

from zope.component.tests.request import Request

from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.app.publisher.browser.i18nfileresource import I18nFileResource

import zope.app.publisher.browser

tests_path = os.path.join(
    os.path.split(zope.app.publisher.browser.__file__)[0],
    'tests')

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'>
   %s
   </zopeConfigure>"""

request = Request(IBrowserPresentation)

class VT(V1, object):
    def publishTraverse(self, request, name):
        try:
            return int(name)
        except:
            return super(VT, self).publishTraverse(request, name)

class Ob:
    __implements__ = IC

ob = Ob()

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.publisher.browser)()

        from zope.component.adapter \
             import provideAdapter
        from zope.app.traversing.defaulttraversable import DefaultTraversable
        from zope.app.interfaces.traversing import ITraversable

        provideAdapter(None, ITraversable, DefaultTraversable)

    def testView(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template % (
            """
            <browser:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC" />
            """
            )))

        self.assertEqual(
            queryView(ob, 'test', request).__class__,
            V1)

    def testDefaultView(self):
        self.assertEqual(queryView(ob, 'test', request,
                                   None), None)

        xmlconfig(StringIO(template % (
            """
            <browser:defaultView name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC" />
            """
            )))

        self.assertEqual(queryView(ob, 'test',
                                   request, None
                                 ).__class__, V1)
        self.assertEqual(getDefaultViewName(ob, request
                                 ), 'test')


    def testSkinView(self):
        self.assertEqual(queryView(ob, 'test', request,
                                   None), None)

        xmlconfig(StringIO(template % (
            """
            <browser:skin name="zmi" layers="zmi default" />
            <browser:view name="test"
                  factory="zope.component.tests.views.VZMI"
                  layer="zmi"
                  for="zope.component.tests.views.IC" />
            <browser:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC" />
            """
            )))

        self.assertEqual(
            queryView(ob, 'test', request).__class__,
            V1)
        self.assertEqual(
            queryView(ob, 'test',
                      Request(IBrowserPresentation, 'zmi')).__class__,
            VZMI)

    def testI18nResource(self):
        self.assertEqual(queryResource(ob, 'test', request,
                                       None),
                         None)

        path1 = os.path.join(tests_path, 'test.pt')
        path2 = os.path.join(tests_path, 'test2.pt')

        xmlconfig(StringIO(template % (
            """
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="fr" file="%s" />
            </browser:i18n-resource>
            """ % (path1, path2)
            )))

        v = getResource(ob, 'test', request)
        self.assertEqual(
            queryResource(ob, 'test', request).__class__,
            I18nFileResource)
        self.assertEqual(v._testData('en'), open(path1, 'rb').read())
        self.assertEqual(v._testData('fr'), open(path2, 'rb').read())

        # translation must be provided for the default language
        config = StringIO(template % (
            """
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="lt" file="%s" />
            </browser:i18n-resource>
            """ % (path1, path2)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

        # files and images can't be mixed
        config = StringIO(template % (
            """
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="fr" image="%s" />
            </browser:i18n-resource>
            """ % (path1, path2)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

    def testInterfaceProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <browser:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <browser:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  allowed_attributes="action"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <browser:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  allowed_attributes="action"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <browser:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  allowed_attributes="action index"
              allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <browser:view name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  allowed_attributes="action index"
                  />
            """
            ))


    def testPageViews(self):
        self.assertEqual(queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'test3.pt')

        xmlconfig(StringIO(template %
            """
            <browser:view
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC">

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action" />
                <browser:page name="test.html" template="%s" />
            </browser:view>
            """ % test3
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')
        v = getView(ob, 'test.html', request)
        self.assertEqual(str(v()), '<html><body><p>done</p></body></html>\n')

    def testNamedViewPageViewsCustomTraversr(self):
        self.assertEqual(queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="test"
                  factory="zope.app.publisher.browser.tests.test_directives.VT"
                  for="zope.component.tests.views.IC">

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action" />
            </browser:view>
            """
            ))

        view = getView(ob, 'test', request)
        view = removeAllProxies(view)
        self.assertEqual(view.browserDefault(request)[1], (u'index.html', ))


        v = view.publishTraverse(request, 'index.html')
        v = removeAllProxies(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(request, 'action.html')
        v = removeAllProxies(v)
        self.assertEqual(v(), 'done')

        v = view.publishTraverse(request, '42')
        self.assertEqual(v, 42)

    def testNamedViewPageViewsNoDefault(self):
        self.assertEqual(queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'test3.pt')

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC">

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action" />
                <browser:page name="test.html" template="%s" />
            </browser:view>
            """ % test3
            ))

        view = getView(ob, 'test', request)
        view = removeAllProxies(view)
        self.assertEqual(view.browserDefault(request)[1], (u'index.html', ))


        v = view.publishTraverse(request, 'index.html')
        v = removeAllProxies(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(request, 'action.html')
        v = removeAllProxies(v)
        self.assertEqual(v(), 'done')
        v = view.publishTraverse(request, 'test.html')
        v = removeAllProxies(v)
        self.assertEqual(str(v()), '<html><body><p>done</p></body></html>\n')

    def testNamedViewPageViewsWithDefault(self):
        self.assertEqual(queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'test3.pt')

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC">

                <browser:defaultPage name="test.html" />
                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action" />
                <browser:page name="test.html" template="%s" />
            </browser:view>
            """ % test3
            ))

        view = getView(ob, 'test', request)
        view = removeAllProxies(view)
        self.assertEqual(view.browserDefault(request)[1], (u'test.html', ))


        v = view.publishTraverse(request, 'index.html')
        v = removeAllProxies(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(request, 'action.html')
        v = removeAllProxies(v)
        self.assertEqual(v(), 'done')
        v = view.publishTraverse(request, 'test.html')
        v = removeAllProxies(v)
        self.assertEqual(str(v()), '<html><body><p>done</p></body></html>\n')

    def testProtectedPageViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
             zope.app.security.registries.metaconfigure.definePermission" />
            </directives>

            <permission id="XXX" title="xxx" />

            <browser:view
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="XXX">

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action"
                              permission="zope.Public" />
            </browser:view>
            """
            ))

        # XXX this seems to be no longer needed
        # Need to "log someone in" to turn on checks
        #from zope.security.securitymanagement import newSecurityManager
        #newSecurityManager('someuser')

        v = getView(ob, 'index.html', request)
        self.assertRaises(Exception, v)
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')

    def testProtectedNamedViewPageViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
             zope.app.security.registries.metaconfigure.definePermission" />
            </directives>

            <permission id="XXX" title="xxx" />

            <browser:view
                  name="test"
                  factory="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public">

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action"
                              permission="XXX" />
            </browser:view>
            """
            ))

        # XXX this seems to be no longer needed
        # Need to "log someone in" to turn on checks
        #from zope.security.securitymanagement import newSecurityManager
        #newSecurityManager('someuser')

        view = getView(ob, 'test', request)
        self.assertEqual(view.browserDefault(request)[1], (u'index.html', ))

        v = view.publishTraverse(request, 'index.html')
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(request, 'action.html')
        self.assertRaises(Exception, v)

    def testSkinnedPageView(self):
        self.assertEqual(queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            """
            <browser:skin name="skinny" layers="layer default" />
            <browser:view
                  factory="zope.component.tests.views.V1">

                <browser:page name="index.html" attribute="index" />
                <browser:page name="index.html" attribute="action"
                              layer="layer"/>
            </browser:view>
            """
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'index.html',
                    Request(IBrowserPresentation, "skinny"))
        self.assertEqual(v(), 'done')

    def testFile(self):
        path = os.path.join(tests_path, 'test.pt')

        self.assertEqual(queryResource(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:resource
                  name="index.html"
                  file="%s"
                  />
            """ % path
            ))

        r = getResource(ob, 'index.html', request)

        # Make sure we can access available attrs and not others
        for n in ('GET', 'HEAD', 'publishTraverse', 'request', '__call__'):
            getattr(r, n)

        self.assertRaises(Exception, getattr, r, '_testData')

        r = removeAllProxies(r)
        self.assertEqual(r._testData(), open(path, 'rb').read())


    def testSkinResource(self):
        self.assertEqual(
            queryResource(ob, 'test', request, None),
            None)

        path = os.path.join(tests_path, 'test.pt')

        xmlconfig(StringIO(template % (
            """
            <browser:skin name="zmi" layers="zmi default" />
            <browser:resource name="test" file="%s" 
                  layer="zmi" />
            """ % path
            )))

        self.assertEqual(queryResource(ob, 'test', request), None)

        r = getResource(ob, 'test', Request(IBrowserPresentation, 'zmi'))
        r = removeAllProxies(r)
        self.assertEqual(r._testData(), open(path, 'rb').read())

    def testtemplate(self):
        path = os.path.join(tests_path, 'test.pt')

        self.assertEqual(queryView(ob, 'index.html', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  for="zope.component.tests.views.IC" />
            """ % path
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')

    def testtemplateWClass(self):
        path = os.path.join(tests_path, 'test2.pt')

        self.assertEqual(queryView(ob, 'index.html', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  class="zope.app.publisher.browser.tests.templateclass."
                  for="zope.component.tests.views.IC" />
            """ % path
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v().strip(), '<html><body><p>42</p></body></html>')

    def testProtectedtemplate(self):
        path = os.path.join(tests_path, 'test.pt')

        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
               zope.app.security.registries.metaconfigure.definePermission" />
            </directives>

            <permission id="XXX" title="xxx" />

            <browser:view
                  name="xxx.html"
                  template="%s"
                  permission="XXX"
                  for="zope.component.tests.views.IC" />
            """ % path
            ))

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  permission="zope.Public"
                  for="zope.component.tests.views.IC" />
            """ % path
            ))

        # XXX This seems to be no longer needed
        # Need to "log someone in" to turn on checks
        #from zope.security.securitymanagement import newSecurityManager
        #newSecurityManager('someuser')

        v = getView(ob, 'xxx.html', request)
        v = ProxyFactory(v)
        self.assertRaises(Exception, v)

        v = getView(ob, 'index.html', request)
        v = ProxyFactory(v)
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')


    def testtemplateNoName(self):
        path = os.path.join(tests_path, 'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <browser:view
                  template="%s"
                  for="zope.component.tests.views.IC"
                  />
            """ % path
            ))

    def testtemplateAndPage(self):
        path = os.path.join(tests_path, 'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  for="zope.component.tests.views.IC"
                  >
               <browser:page name="foo.html" attribute="index" />
            </browser:view>
            """ % path
            ))



def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
