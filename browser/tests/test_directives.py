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

from zope.interface import Interface, implements

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.component.tests.views import IC, V1, VZMI
from zope.component import getView, queryView, queryResource
from zope.component import getDefaultViewName, getResource
from zope.app.services.servicenames import Permissions
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.proxy import ProxyFactory
from zope.proxy import removeAllProxies
import zope.configuration

from zope.app.publisher.browser.globalbrowsermenuservice import \
    globalBrowserMenuService
from zope.component.tests.request import Request
from zope.publisher.browser import TestRequest

from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.app.publisher.browser.i18nfileresource import I18nFileResource

import zope.app.publisher.browser
from zope.component.service import serviceManager
from zope.app.interfaces.security import IPermissionService
from zope.app.security.registries.permissionregistry import permissionRegistry

from zope.component.service import serviceManager
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.app.interfaces.security import IPermissionService

from zope.publisher.interfaces.browser import IBrowserPublisher

tests_path = os.path.join(
    os.path.split(zope.app.publisher.browser.__file__)[0],
    'tests')

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'>
   %s
   </configure>"""

request = Request(IBrowserPresentation)

class VT(V1, object):
    def publishTraverse(self, request, name):
        try:
            return int(name)
        except:
            return super(VT, self).publishTraverse(request, name)

class Ob:
    implements(IC)

ob = Ob()

class NCV(object):
    "non callable view"

    def __init__(self, context, request):
        pass

class CV(NCV):
    "callable view"
    def __call__(self):
        pass


class C_w_implements(NCV):

    implements(Interface)

    def index(self):
        return self

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', zope.app.publisher.browser)()

        from zope.component.adapter import provideAdapter
        from zope.app.traversing.adapters import DefaultTraversable
        from zope.app.interfaces.traversing import ITraversable

        provideAdapter(None, ITraversable, DefaultTraversable)

    def testPage(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template % (
            """
            <browser:page name="test"
                          class="zope.component.tests.views.V1"
                          for="zope.component.tests.views.IC"
                          permission="zope.Public"
                          attribute="index"
                          />
            """
            )))

        v = queryView(ob, 'test', request)
        self.assert_(issubclass(v.__class__, V1))

    def testPageWithClassWithMenu(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_menu" title="Test menu" usage="objectview"/>
            <browser:page name="test"
                          class="zope.component.tests.views.V1"
                          for="zope.component.tests.views.IC"
                          permission="zope.Public"
                          template="%s" 
                          menu="test_menu"
                          title="Test View"
                          />
            """ % testusage
            )))

        menuItem = globalBrowserMenuService.getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testPageWithClassWithUsage(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:page name="test"
                          class="zope.component.tests.views.V1"
                          for="zope.component.tests.views.IC"
                          permission="zope.Public"
                          template="%s" 
                          usage="objectview"
                          />
            """ % testusage
            )))

        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testPageWithClassWithMenuAndUsage(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_menu" title="Test menu" usage="overridden"/>
            <browser:page name="test"
                          class="zope.component.tests.views.V1"
                          for="zope.component.tests.views.IC"
                          permission="zope.Public"
                          template="%s" 
                          menu="test_menu"
                          title="Test View"
                          usage="objectview"
                          />
            """ % testusage
            )))

        menuItem = globalBrowserMenuService.getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testPageWithTemplateWithMenu(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_menu" title="Test menu" usage="objectview"/>
            <browser:page name="test"
                          for="zope.component.tests.views.IC"
                          permission="zope.Public"
                          template="%s" 
                          menu="test_menu"
                          title="Test View"
                          />
            """ % testusage
            )))

        menuItem = globalBrowserMenuService.getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testPageWithTemplateWithUsage(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:page name="test"
                          for="zope.component.tests.views.IC"
                          permission="zope.Public"
                          template="%s" 
                          usage="objectview"
                          />
            """ % testusage
            )))

        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testPageWithTemplateWithMenuAndUsage(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_menu" title="Test menu" usage="overridden"/>
            <browser:page name="test"
                          for="zope.component.tests.views.IC"
                          permission="zope.Public"
                          template="%s" 
                          menu="test_menu"
                          title="Test View"
                          usage="objectview"
                          />
            """ % testusage
            )))

        menuItem = globalBrowserMenuService.getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testPageInPagesWithTemplateWithMenu(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_menu" title="Test menu" usage="objectview"/>
            <browser:pages for="zope.component.tests.views.IC"
                          permission="zope.Public">
                <browser:page name="test"
                              template="%s" 
                              menu="test_menu"
                              title="Test View"
                              />
            </browser:pages>                  
            """ % testusage
            )))

        menuItem = globalBrowserMenuService.getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testPageInPagesWithClassWithMenu(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        testusage = os.path.join(tests_path, 'testusage.pt')
                         

        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_menu" title="Test menu" usage="objectview"/>
            <browser:pages for="zope.component.tests.views.IC"
                           class="zope.component.tests.views.V1"
                           permission="zope.Public">
                <browser:page name="test"
                              template="%s" 
                              menu="test_menu"
                              title="Test View"
                              />
            </browser:pages>                  
            """ % testusage
            )))

        menuItem = globalBrowserMenuService.getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = queryView(ob, 'test', request)
        self.assertEqual(v(), "objectview\n")

    def testDefaultView(self):
        self.assertEqual(queryView(ob, 'test', request,
                                   None), None)

        xmlconfig(StringIO(template % (
            """
            <browser:defaultView name="test"
                                 for="zope.component.tests.views.IC" />
            """
            )))

        self.assertEqual(getDefaultViewName(ob, request
                                 ), 'test')


    def testSkinPage(self):
        self.assertEqual(queryView(ob, 'test', request,
                                   None), None)

        xmlconfig(StringIO(template % (
            """
            <browser:skin name="zmi" layers="zmi default" />
            <browser:page name="test"
                  class="zope.component.tests.views.VZMI"
                  layer="zmi"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  attribute="index"
                  />
            <browser:page name="test"
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  attribute="index"
                  />
            """
            )))

        v = queryView(ob, 'test', request)
        self.assert_(issubclass(v.__class__, V1))
        v = queryView(ob, 'test', Request(IBrowserPresentation, 'zmi'))
        self.assert_(issubclass(v.__class__, VZMI))

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

    def testInterfaceProtectedPage(self):
        xmlconfig(StringIO(template %
            """
            <browser:page name="test"
                  class="zope.component.tests.views.V1"
                  attribute="index"
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

    def testAttributeProtectedPage(self):
        xmlconfig(StringIO(template %
            """
            <browser:page name="test"
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  attribute="action"
                  permission="zope.Public"
                  allowed_attributes="action"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedPage(self):
        xmlconfig(StringIO(template %
            """
            <browser:page name="test"
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  attribute="index"
                  allowed_attributes="action"
                  allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedPage(self):
        xmlconfig(StringIO(template %
            """
            <browser:page name="test"
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  attribute="index"
                  permission="zope.Public"
                  allowed_attributes="action index"
                  allowed_interface="zope.component.tests.views.IV"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def test_class_w_implements(self):
        xmlconfig(StringIO(template %
            """
            <browser:page
                  name="test"
                  class="
             zope.app.publisher.browser.tests.test_directives.C_w_implements"
                  for="zope.component.tests.views.IC"
                  attribute="index"
                  permission="zope.Public"
                  />
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), v)
        self.assert_(IBrowserPublisher.isImplementedBy(v))

    def testIncompleteProtectedPageNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <browser:page name="test"
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  attribute="index"
                  allowed_attributes="action index"
                  />
            """
            ))


    def testPageViews(self):
        self.assertEqual(queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'test3.pt')

        xmlconfig(StringIO(template %
            """
            <browser:pages
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  >

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action" />
                <browser:page name="test.html" template="%s" />
            </browser:pages>
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
                  class="zope.app.publisher.browser.tests.test_directives.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  >

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


    def testNamedViewNoPagesForCallable(self):
        self.assertEqual(queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="test"
                  class="zope.app.publisher.browser.tests.test_directives.CV"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  />
            """
            ))

        view = getView(ob, 'test', request)
        view = removeAllProxies(view)
        self.assertEqual(view.browserDefault(request), (view, ()))

    def testNamedViewNoPagesForNonCallable(self):
        self.assertEqual(queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="test"
                  class="zope.app.publisher.browser.tests.test_directives.NCV"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  />
            """
            ))

        view = getView(ob, 'test', request)
        view = removeAllProxies(view)
        self.assertEqual(getattr(view, 'browserDefault', None), None)

    def testNamedViewPageViewsNoDefault(self):
        self.assertEqual(queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'test3.pt')

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="test"
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  >

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
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  >

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

        serviceManager.defineService(Permissions, IPermissionService)
        serviceManager.provideService(Permissions, permissionRegistry)
        permissionRegistry.definePermission('p', 'P')


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

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:pages
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.TestPermission"
                  >

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action" />
            </browser:pages>
            """
            ))

        v = getView(ob, 'index.html', request)
        v = ProxyFactory(v)
        self.assertRaises(Exception, v)
        v = getView(ob, 'action.html', request)
        v = ProxyFactory(v)
        self.assertRaises(Exception, v)

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

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:view
                  name="test"
                  class="zope.component.tests.views.V1"
                  for="zope.component.tests.views.IC"
                  permission="zope.Public"
                  >

                <browser:page name="index.html" attribute="index" />
                <browser:page name="action.html" attribute="action" />
            </browser:view>
            """
            ))

        # XXX this seems to be no longer needed
        # Need to "log someone in" to turn on checks
        #from zope.security.management import newSecurityManager
        #newSecurityManager('someuser')

        view = getView(ob, 'test', request)
        self.assertEqual(view.browserDefault(request)[1], (u'index.html', ))

        v = view.publishTraverse(request, 'index.html')
        self.assertEqual(v(), 'V1 here')

    def testSkinnedPageView(self):
        self.assertEqual(queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            """
            <browser:skin name="skinny" layers="layer default" />
            <browser:pages
                  for="*"
                  class="zope.component.tests.views.V1"
                  permission="zope.Public"
                  >

                <browser:page name="index.html" attribute="index" />
            </browser:pages>
            <browser:pages
                  for="*"
                  class="zope.component.tests.views.V1"
                  layer="layer"
                  permission="zope.Public"
                  >

                <browser:page name="index.html" attribute="action" />
            </browser:pages>
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

    def test_template_page(self):
        path = os.path.join(tests_path, 'test.pt')

        self.assertEqual(queryView(ob, 'index.html', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:page
                  name="index.html"
                  template="%s"
                  permission="zope.Public"
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
            <browser:page
                  name="index.html"
                  template="%s"
                  permission="zope.Public"
          class="zope.app.publisher.browser.tests.templateclass.templateclass"
                  for="zope.component.tests.views.IC" />
            """ % path
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v().strip(), '<html><body><p>42</p></body></html>')

    def testProtectedtemplate(self):

        serviceManager.defineService(Permissions, IPermissionService)
        serviceManager.provideService(Permissions, permissionRegistry)
        
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

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:page
                  name="xxx.html"
                  template="%s"
                  permission="zope.TestPermission"
                  for="zope.component.tests.views.IC" />
            """ % path
            ))

        xmlconfig(StringIO(template %
            """
            <browser:page
                  name="index.html"
                  template="%s"
                  permission="zope.Public"
                  for="zope.component.tests.views.IC" />
            """ % path
            ))

        # XXX This seems to be no longer needed
        # Need to "log someone in" to turn on checks
        #from zope.security.management import newSecurityManager
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
            <browser:page
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
                  permission="zope.Public"
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
