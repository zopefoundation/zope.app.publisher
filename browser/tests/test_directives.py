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
"""'browser' namespace directive tests

$Id$
"""
import os
import unittest
from cStringIO import StringIO

from zope.interface import Interface, implements, directlyProvides, providedBy

import zope.security.management
from zope.component.service import serviceManager
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import ISkin, IDefaultSkin
from zope.security.proxy import removeSecurityProxy, ProxyFactory
from zope.testing.doctestunit import DocTestSuite

import zope.app.publisher.browser
from zope.app import zapi
from zope.app.component.tests.views import IC, V1, VZMI, R1, IV
from zope.app.publisher.browser.fileresource import FileResource
from zope.app.publisher.browser.i18nfileresource import I18nFileResource
from zope.app.publisher.browser.menu import getFirstMenuItem
from zope.app.publisher.interfaces.browser import IMenuItemType
from zope.app.security.permission import Permission 
from zope.app.security.interfaces import IPermission 
from zope.app.tests import placelesssetup
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.interfaces import ITraversable


tests_path = os.path.join(
    os.path.dirname(zope.app.publisher.browser.__file__),
    'tests')

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


request = TestRequest()

class VT(V1, object):
    def publishTraverse(self, request, name):
        try:
            return int(name)
        except:
            return super(VT, self).publishTraverse(request, name)

class Ob(object):
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
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.publisher.browser)()
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)


    def testPage(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template % (
            '''
            <browser:page
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                attribute="index"
                />
            '''
            )))

        v = zapi.queryView(ob, 'test', request)
        self.assert_(issubclass(v.__class__, V1))

    def testPageWithClassWithMenu(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')
                         

        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu" />
            <browser:page
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                template="%s" 
                menu="test_menu"
                title="Test View"
                />
            ''' % testtemplate
            )))
        test_menu = zapi.getUtility(IMenuItemType, 'test_menu')
        menuItem = getFirstMenuItem(test_menu, ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = zapi.queryView(ob, 'test', request)
        self.assertEqual(v(), "<html><body><p>test</p></body></html>\n")


    def testPageWithTemplateWithMenu(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')
                         
        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu"/>
            <browser:page
                name="test"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                template="%s" 
                menu="test_menu"
                title="Test View"
                />
            ''' % testtemplate
            )))

        test_menu = zapi.getUtility(IMenuItemType, 'test_menu')
        menuItem = getFirstMenuItem(test_menu, ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = zapi.queryView(ob, 'test', request)
        self.assertEqual(v(), "<html><body><p>test</p></body></html>\n")


    def testPageInPagesWithTemplateWithMenu(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')

        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu" />
            <browser:pages
                for="zope.app.component.tests.views.IC"
                permission="zope.Public">
              <browser:page
                  name="test"
                  template="%s" 
                  menu="test_menu"
                  title="Test View"
                  />
            </browser:pages>                  
            ''' % testtemplate
            )))

        test_menu = zapi.getUtility(IMenuItemType, 'test_menu')
        menuItem = getFirstMenuItem(test_menu, ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = zapi.queryView(ob, 'test', request)
        self.assertEqual(v(), "<html><body><p>test</p></body></html>\n")


    def testPageInPagesWithClassWithMenu(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        testtemplate = os.path.join(tests_path, 'testfiles', 'test.pt')
                         

        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu" />
            <browser:pages
                for="zope.app.component.tests.views.IC"
                class="zope.app.component.tests.views.V1"
                permission="zope.Public">
              <browser:page
                  name="test"
                  template="%s" 
                  menu="test_menu"
                  title="Test View"
                  />
            </browser:pages>                  
            ''' % testtemplate
            )))

        test_menu = zapi.getUtility(IMenuItemType, 'test_menu')
        menuItem = getFirstMenuItem(test_menu, ob, TestRequest())
        self.assertEqual(menuItem["title"], "Test View")
        self.assertEqual(menuItem["action"], "@@test")
        v = zapi.queryView(ob, 'test', request)
        self.assertEqual(v(), "<html><body><p>test</p></body></html>\n")

    def testDefaultView(self):
        self.assertEqual(zapi.queryView(ob, 'test', request,
                                   None), None)

        xmlconfig(StringIO(template % (
            '''
            <browser:defaultView
                name="test"
                for="zope.app.component.tests.views.IC" />
            '''
            )))

        self.assertEqual(zapi.getDefaultViewName(ob, request
                                 ), 'test')

    def testSkinResource(self):
        self.assertEqual(
            zapi.queryResource('test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            '''
            <browser:layer name="zmi" />
            <browser:skin name="zmi" layers="zmi" />
            <browser:resource
                name="test"
                factory="zope.app.component.tests.views.RZMI"
                layer="zmi" />
            <browser:resource
                name="test"
                factory="zope.app.component.tests.views.R1" />
            '''
            )))

        self.assertEqual(
            zapi.queryResource('test', request, None).__class__, R1)
        zmi = zapi.getUtility(ISkin, 'zmi')
        self.assertEqual(
            zapi.queryResource('test', TestRequest(skin=zmi), None).__class__,
            RZMI)

    def testDefaultSkin(self):
        request = TestRequest()

        self.assertEqual(zapi.queryView(ob, 'test', request, None), None)
        xmlconfig(StringIO(template % (
            '''
            <browser:layer name="zmi" />
            <browser:skin name="zmi" layers="zmi" />
            <browser:defaultSkin name="zmi" />
            <browser:page name="test"
                class="zope.app.component.tests.views.VZMI"
                layer="zmi"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                attribute="index"
                />
            <browser:page name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                attribute="index"
                />
            '''
            )))

        # Simulate Zope Publication behavior in beforeTraversal()
        adapters = zapi.getService(zapi.servicenames.Adapters)
        skin = adapters.lookup((providedBy(request),), IDefaultSkin, '')
        directlyProvides(request, skin)

        v = zapi.queryView(ob, 'test', request)
        self.assert_(issubclass(v.__class__, VZMI))

    def testSkinPage(self):
        self.assertEqual(zapi.queryView(ob, 'test', request, None), None)

        xmlconfig(StringIO(template % (
            '''
            <browser:layer name="zmi" />
            <browser:skin name="zmi" layers="zmi" />
            <browser:page name="test"
                class="zope.app.component.tests.views.VZMI"
                layer="zmi"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                attribute="index"
                />
            <browser:page name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                attribute="index"
                />
            '''
            )))

        v = zapi.queryView(ob, 'test', request)
        self.assert_(issubclass(v.__class__, V1))
        zmi = zapi.getUtility(ISkin, 'zmi')
        v = zapi.queryView(ob, 'test', TestRequest(skin=zmi))
        self.assert_(issubclass(v.__class__, VZMI))

    def testI18nResource(self):
        self.assertEqual(zapi.queryResource('test', request, None), None)

        path1 = os.path.join(tests_path, 'testfiles', 'test.pt')
        path2 = os.path.join(tests_path, 'testfiles', 'test2.pt')

        xmlconfig(StringIO(template % (
            '''
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="fr" file="%s" />
            </browser:i18n-resource>
            ''' % (path1, path2)
            )))

        v = zapi.getResource('test', request)
        self.assertEqual(
            zapi.queryResource('test', request).__class__,
            I18nFileResource)
        self.assertEqual(v._testData('en'), open(path1, 'rb').read())
        self.assertEqual(v._testData('fr'), open(path2, 'rb').read())

        # translation must be provided for the default language
        config = StringIO(template % (
            '''
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="lt" file="%s" />
            </browser:i18n-resource>
            ''' % (path1, path2)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

        # files and images can't be mixed
        config = StringIO(template % (
            '''
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="fr" image="%s" />
            </browser:i18n-resource>
            ''' % (path1, path2)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

    def testInterfaceProtectedPage(self):
        xmlconfig(StringIO(template %
            '''
            <browser:page name="test"
                class="zope.app.component.tests.views.V1"
                attribute="index"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                allowed_interface="zope.app.component.tests.views.IV"
                />
            '''
            ))

        v = zapi.getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedPage(self):
        xmlconfig(StringIO(template %
            '''
            <browser:page name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                attribute="action"
                permission="zope.Public"
                allowed_attributes="action"
                />
            '''
            ))

        v = zapi.getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedPage(self):
        xmlconfig(StringIO(template %
            '''
            <browser:page name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                attribute="index"
                allowed_attributes="action"
                allowed_interface="zope.app.component.tests.views.IV"
                />
            '''
            ))

        v = zapi.getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedPage(self):
        xmlconfig(StringIO(template %
            '''
            <browser:page name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                attribute="index"
                permission="zope.Public"
                allowed_attributes="action index"
                allowed_interface="zope.app.component.tests.views.IV"
                />
            '''
            ))

        v = zapi.getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def test_class_w_implements(self):
        xmlconfig(StringIO(template %
            '''
            <browser:page
                name="test"
                class="
             zope.app.publisher.browser.tests.test_directives.C_w_implements"
                for="zope.app.component.tests.views.IC"
                attribute="index"
                permission="zope.Public"
                />
            '''
            ))

        v = zapi.getView(ob, 'test', request)
        self.assertEqual(v.index(), v)
        self.assert_(IBrowserPublisher.providedBy(v))

    def testIncompleteProtectedPageNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            '''
            <browser:page name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                attribute="index"
                allowed_attributes="action index"
                />
            '''
            ))


    def testPageViews(self):
        self.assertEqual(zapi.queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'testfiles', 'test3.pt')

        xmlconfig(StringIO(template %
            '''
            <browser:pages
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
              <browser:page name="test.html" template="%s" />
            </browser:pages>
            ''' % test3
            ))

        v = zapi.getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = zapi.getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')
        v = zapi.getView(ob, 'test.html', request)
        self.assertEqual(str(v()), '<html><body><p>done</p></body></html>\n')

    def testNamedViewPageViewsCustomTraversr(self):
        self.assertEqual(zapi.queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.publisher.browser.tests.test_directives.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
            </browser:view>
            '''
            ))

        view = zapi.getView(ob, 'test', request)
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(request)[1], (u'index.html', ))


        v = view.publishTraverse(request, 'index.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(request, 'action.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'done')


    def testNamedViewNoPagesForCallable(self):
        self.assertEqual(zapi.queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.publisher.browser.tests.test_directives.CV"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                />
            '''
            ))

        view = zapi.getView(ob, 'test', request)
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(request), (view, ()))

    def testNamedViewNoPagesForNonCallable(self):
        self.assertEqual(zapi.queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.publisher.browser.tests.test_directives.NCV"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                />
            '''
            ))

        view = zapi.getView(ob, 'test', request)
        view = removeSecurityProxy(view)
        self.assertEqual(getattr(view, 'browserDefault', None), None)

    def testNamedViewPageViewsNoDefault(self):
        self.assertEqual(zapi.queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'testfiles', 'test3.pt')

        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                >

              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
              <browser:page name="test.html" template="%s" />
            </browser:view>
            ''' % test3
            ))

        view = zapi.getView(ob, 'test', request)
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(request)[1], (u'index.html', ))


        v = view.publishTraverse(request, 'index.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(request, 'action.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'done')
        v = view.publishTraverse(request, 'test.html')
        v = removeSecurityProxy(v)
        self.assertEqual(str(v()), '<html><body><p>done</p></body></html>\n')

    def testNamedViewPageViewsWithDefault(self):
        self.assertEqual(zapi.queryView(ob, 'test', request), None)
        test3 = os.path.join(tests_path, 'testfiles', 'test3.pt')

        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                >
            
              <browser:defaultPage name="test.html" />
              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
              <browser:page name="test.html" template="%s" />
            </browser:view>
            ''' % test3
            ))

        view = zapi.getView(ob, 'test', request)
        view = removeSecurityProxy(view)
        self.assertEqual(view.browserDefault(request)[1], (u'test.html', ))


        v = view.publishTraverse(request, 'index.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'V1 here')
        v = view.publishTraverse(request, 'action.html')
        v = removeSecurityProxy(v)
        self.assertEqual(v(), 'done')
        v = view.publishTraverse(request, 'test.html')
        v = removeSecurityProxy(v)
        self.assertEqual(str(v()), '<html><body><p>done</p></body></html>\n')

    def testTraversalOfPageForView(self):
        """Tests proper traversal of a page defined for a view."""
        
        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public" />

            <browser:page name="index.html"
                for="zope.app.component.tests.views.IV" 
                class="zope.app.publisher.browser.tests.test_directives.CV"
                permission="zope.Public" />
            '''
            ))

        view = zapi.getView(ob, 'test', request)
        view = removeSecurityProxy(view)
        view.publishTraverse(request, 'index.html')
        
    def testTraversalOfPageForViewWithPublishTraverse(self):
        """Tests proper traversal of a page defined for a view.
        
        This test is different from testTraversalOfPageForView in that it
        tests the behavior on a view that has a publishTraverse method --
        the implementation of the lookup is slightly different in such a
        case.
        """
        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.publisher.browser.tests.test_directives.VT"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public" />

            <browser:page name="index.html"
                for="zope.app.component.tests.views.IV" 
                class="zope.app.publisher.browser.tests.test_directives.CV"
                permission="zope.Public" />
            '''
            ))

        view = zapi.getView(ob, 'test', request)
        view = removeSecurityProxy(view)
        view.publishTraverse(request, 'index.html')

    def testProtectedPageViews(self):
        ztapi.provideUtility(IPermission, Permission('p', 'P'), 'p')

        request = TestRequest()
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            '''
            <include package="zope.app.security" file="meta.zcml" />
            
            <permission id="zope.TestPermission" title="Test permission" />

            <browser:pages
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.TestPermission"
                >
             
              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
            </browser:pages>
            '''
            ))

        v = zapi.getView(ob, 'index.html', request)
        v = ProxyFactory(v)
        zope.security.management.getInteraction().add(request)
        self.assertRaises(Exception, v)
        v = zapi.getView(ob, 'action.html', request)
        v = ProxyFactory(v)
        self.assertRaises(Exception, v)

    def testProtectedNamedViewPageViews(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            '''
            <include package="zope.app.security" file="meta.zcml" />

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:view
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                >
             
              <browser:page name="index.html" attribute="index" />
              <browser:page name="action.html" attribute="action" />
            </browser:view>
            '''
            ))

        view = zapi.getView(ob, 'test', request)
        self.assertEqual(view.browserDefault(request)[1], (u'index.html', ))

        v = view.publishTraverse(request, 'index.html')
        self.assertEqual(v(), 'V1 here')

    def testSkinnedPageView(self):
        self.assertEqual(zapi.queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            '''
            <browser:layer name="layer" />
            <browser:skin name="skinny" layers="layer" />
            <browser:pages
                for="*"
                class="zope.app.component.tests.views.V1"
                permission="zope.Public"
                >
             
              <browser:page name="index.html" attribute="index" />
            </browser:pages>
            <browser:pages
                for="*"
                class="zope.app.component.tests.views.V1"
                layer="layer"
                permission="zope.Public"
                >
            
              <browser:page name="index.html" attribute="action" />
            </browser:pages>
            '''
            ))

        v = zapi.getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        skinny = zapi.getUtility(ISkin, 'skinny')
        v = zapi.getView(ob, 'index.html', TestRequest(skin=skinny))
        self.assertEqual(v(), 'done')

    def testFile(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        self.assertEqual(zapi.queryResource('test', request), None)

        xmlconfig(StringIO(template %
            '''
            <browser:resource
                name="index.html"
                file="%s"
                />
            ''' % path
            ))

        r = zapi.getResource('index.html', request)
        self.assertEquals(r.__class__, FileResource)
        r = ProxyFactory(r)
        self.assertEqual(r.__name__, "index.html")

        # Make sure we can access available attrs and not others
        for n in ('GET', 'HEAD', 'publishTraverse', 'request', '__call__'):
            getattr(r, n)
        self.assertEqual(r.__name__, "index.html")

        self.assertRaises(Exception, getattr, r, '_testData')

        r = removeSecurityProxy(r)
        self.assert_(r.__class__ is FileResource)
        self.assertEqual(r._testData(), open(path, 'rb').read())


    def testSkinResource(self):
        self.assertEqual(
            zapi.queryResource('test', request, None),
            None)

        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        xmlconfig(StringIO(template % (
            '''
            <browser:layer name="zmi" />
            <browser:skin name="zmi" layers="zmi" />
            <browser:resource name="test" file="%s" 
                  layer="zmi" />
            ''' % path
            )))

        self.assertEqual(zapi.queryResource('test', request), None)

        zmi = zapi.getUtility(ISkin, 'zmi')
        r = zapi.getResource('test', TestRequest(skin=zmi))
        r = removeSecurityProxy(r)
        self.assertEqual(r._testData(), open(path, 'rb').read())

    def test_template_page(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        self.assertEqual(zapi.queryView(ob, 'index.html', request),
                         None)

        xmlconfig(StringIO(template %
            '''
            <browser:page
                name="index.html"
                template="%s"
                permission="zope.Public"
                for="zope.app.component.tests.views.IC" />
            ''' % path
            ))

        v = zapi.getView(ob, 'index.html', request)
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')

    def testtemplateWClass(self):
        path = os.path.join(tests_path, 'testfiles', 'test2.pt')

        self.assertEqual(zapi.queryView(ob, 'index.html', request),
                         None)

        xmlconfig(StringIO(template %
            '''
            <browser:page
                name="index.html"
                template="%s"
                permission="zope.Public"
          class="zope.app.publisher.browser.tests.templateclass.templateclass"
                for="zope.app.component.tests.views.IC" />
            ''' % path
            ))

        v = zapi.getView(ob, 'index.html', request)
        self.assertEqual(v().strip(), '<html><body><p>42</p></body></html>')

    def testProtectedtemplate(self):

        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        request = TestRequest()
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            '''
            <include package="zope.app.security" file="meta.zcml" />

            <permission id="zope.TestPermission" title="Test permission" />

            <browser:page
                name="xxx.html"
                template="%s"
                permission="zope.TestPermission"
                for="zope.app.component.tests.views.IC" />
            ''' % path
            ))

        xmlconfig(StringIO(template %
            '''
            <browser:page
                name="index.html"
                template="%s"
                permission="zope.Public"
                for="zope.app.component.tests.views.IC" />
            ''' % path
            ))

        v = zapi.getView(ob, 'xxx.html', request)
        v = ProxyFactory(v)
        zope.security.management.getInteraction().add(request)
        self.assertRaises(Exception, v)

        v = zapi.getView(ob, 'index.html', request)
        v = ProxyFactory(v)
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')


    def testtemplateNoName(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            '''
            <browser:page
                template="%s"
                for="zope.app.component.tests.views.IC"
                />
            ''' % path
            ))

    def testtemplateAndPage(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            '''
            <browser:view
                name="index.html"
                template="%s"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                >
              <browser:page name="foo.html" attribute="index" />
            </browser:view>
            ''' % path
            ))

    def testViewThatProvidesAnInterface(self):
        request = TestRequest()
        self.assertEqual(zapi.queryView(ob, 'test', request, None), None)

        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                />
            '''
            ))

        v = zapi.queryView(ob, 'test', request, providing=IV)
        self.assertEqual(v, None)

        xmlconfig(StringIO(template %
            '''
            <browser:view
                name="test"
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                provides="zope.app.component.tests.views.IV"
                permission="zope.Public"
                />
            '''
            ))

        v = zapi.queryView(ob, 'test', request, providing=IV)
        self.assert_(isinstance(v, V1))

    def testUnnamedViewThatProvidesAnInterface(self):
        request = TestRequest()
        self.assertEqual(zapi.queryView(ob, '', request, None, providing=IV),
                         None)

        xmlconfig(StringIO(template %
            '''
            <browser:view
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                permission="zope.Public"
                />
            '''
            ))

        v = zapi.queryView(ob, '', request, None, providing=IV)
        self.assertEqual(v, None)

        xmlconfig(StringIO(template %
            '''
            <browser:view
                class="zope.app.component.tests.views.V1"
                for="zope.app.component.tests.views.IC"
                provides="zope.app.component.tests.views.IV"
                permission="zope.Public"
                />
            '''
            ))

        v = zapi.queryView(ob, '', request, None, providing=IV)

        self.assert_(isinstance(v, V1))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        DocTestSuite('zope.app.publisher.browser.metaconfigure',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown)
        ))

if __name__=='__main__':
    unittest.main(defaultTest="test_suite")
