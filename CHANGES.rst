=========
 CHANGES
=========

5.0 (2023-02-10)
================

- Add support for Python 3.9, 3.10, 3.11.

- Drop support for Python 2.7, 3.5, 3.6.

- Make ``.xmlrpc.testing.ServerProxy`` set an appropriate ``Host`` header in
  its request, allowing WSGI applications that serve multiple virtual hosts
  to tell the difference between them.


4.3.1 (2020-06-08)
==================

- Fix handling of HTTP body in ``.xmlrpc.testing`` to enable characters
  beyond ASCII.
  (`#11 <https://github.com/zopefoundation/zope.app.publisher/issues/11>`_)


4.3.0 (2020-05-12)
==================

- Support options *use_datetime* (Python >= 2.7) and *use_builtin_types*
  (`Python >= 3.5`) in ``.xmlrpc.testing.ServerProxy``.


4.2.0 (2019-12-05)
==================

- Move XMLRPC testing infrastructure from ``.xmlrpc.tests`` to
  ``.xmlrpc.testing`` and make it reusable by requiring the WSGI app to be
  provided. Use the ``testing`` extra from `setup.py` to use this testing
  infrastructure.
  (`#8 <https://github.com/zopefoundation/zope.app.publisher/pull/8>`_)

- Add support for Python 3.8.

- Drop support for Python 3.4.


4.1.0 (2018-10-22)
==================

- Add support for Python 3.7.


4.0.0 (2017-05-05)
==================

- Add support for Python 3.4, 3.5, 3.6 and PyPy.

- Replaced an undeclared test dependency on zope.app.authentication with
  zope.password.

- Removed test dependency on ``zope.app.testing``,
  ``zope.app.zcmlfiles`` and others.

3.10.2 (2010-09-14)
===================

- Remove a testing dependency on zope.app.securitypolicy.

3.10.1 (2010-01-08)
===================

- Fix tests using a newer zope.publisher that requires zope.login.

3.10.0 (2009-08-31)
===================

- Fix test dependency on zope.container, now we depend on
  zope.container >= 3.9.

3.9.0 (2009-08-27)
==================

Refactor package, spliting it to several new packages:

   * ``zope.browserresource`` - the resources mechanism was moved here, see its
     CHANGES.txt for more information about changes during move.

   * ``zope.ptresource`` - the page template resource was moved into another
     package so zope.browserresource doesn't depend on any templating system.
     See zope.ptresource's CHANGES.txt for more information.

   * ``zope.browsermenu`` - the menu mechanism was moved here completely.

   * ``zope.browserpage`` - the browser:page directive and friends were
     moved here. Also, these directives don't depend hardly on menu system
     anymore, so they simply ignore the "menu" argument when zope.browsermenu
     is not available.

Backward-compatibility imports are provided, so there should not be much impact
for those who uses old imports.

The CacheableBrowserLanguages and ModifiableBrowserLanguages adapters were
moved into ``zope.publisher`` package, as well as browser:defaultSkin and
browser:defaultView ZCML directives and ZCML class configuration for
zope.publisher classes.

ZCML registrations of IXMLRPCPublisher adapters for zope.container were moved
into zope.container for now.


3.8.4 (2009-07-23)
==================

- Added dependency on ``zope.app.pagetemplate``, it is used by
  ``zope.app.publisher.browser.viewmeta``.

3.8.3 (2009-06-18)
==================

- Bugfix: Fix ``IAbsoluteURL`` for ``IResource`` configuration. The latest
  release was moving the url generation for resources to an adapter which was
  a good idea. But the adapter was configured for
  ``IDefaultBrowserLayer``. This means every existing project which dosen't
  use ``IDefaultBrowserLayer`` will get a wrong ``IAbsoluteURL`` adapter and
  is loosing the ``@@`` part in the resource url.


3.8.2 (2009-06-16)
==================

- Remove test dependency on ``zope.app.pagetemplate``.

- Calling a resource to get its URL now uses ``IAbsoluteURL``.

3.8.1 (2009-05-25)
==================

- Updated to use ``zope.pagetemplate.engine`` module (requires versino
  3.5.0 or later), instead of ``zope.app.pagetemplate`` precursor.

- Replaced ``zope.deprecation`` dependency with BBB imports

3.8.0 (2009-05-23)
==================

- There is no direct dependency on zope.app.component anymore (even in
  the tests).

- Moved the publicationtraverse module to zope.traversing, removing the
  zope.app.publisher -> zope.app.publication dependency (which was a
  cycle).

- Moved the DefaultViewName API from zope.app.publisher.browser to
  zope.publisher.defaultview, making it accessible to other packages
  that need it.

3.7.0 (2009-05-22)
==================

- Use zope.componentvocabulary instead of zope.app.component
  (except for tests and IBasicViewInformation).

- Use zope.browser for IAdding interface (instead of zope.app.container)

- Update references to ``zope.app.component.tests.views`` to point to the new
  locations in ``zope.component.testfiles.views``.

3.6.2 (2009-03-18)
==================

- Register ``IModifiableUserPreferredLanguages`` adapter in the ZCML
  configuration of ``zope.app.publisher.browser`` package. This was previously
  done by ``zope.app.i18n``.

3.6.1 (2009-03-12)
==================

- Remove deprecated code.

- Adapt to removal of deprecated interfaces from zope.component.interfaces.
  The IResource is now moved to zope.app.publisher.interfaces. The IView
  and IDefaultViewName is now in zope.publisher.interfaces. The IPresentation
  interface was removed completely.

3.6.0 (2009-01-31)
==================

- Use zope.container instead of zope.app.container.

- Use zope.site.folder instead of zope.app.folder.

3.5.3 (2009-01-27)
==================

- Finally removed <browser:skin> and <browser:layer> that were marked as
  deprecated in 2006/02.

3.5.2 (2008-12-06)
==================

- Added possibility to specify custom item class in menuItem, subMenuItem
  and addMenuItem directives using the ``item_class`` argument (LP #291865).

- Menu items registered with <browser:page/> were not re-registered after the
  first functional test layer ran. In any subsequent functional test layer the
  items where not availabe (introduced in 3.5.0a3).

- Added a hook to specify a different BaseURL for resources. This makes sense
  if you want to put resources on a Content Delivery Network. All you need to
  do is to register an named Adapter 'resource' that implements IAbsoluteURL.

3.5.1 (2008-10-13)
==================

- Removed usage of deprecated LayerField from zope.app.component.back35.

3.5.0 (2008-08-05)
==================

- Refactored code to provide more hooks when deriving code from this pacakge.

  * A resource's URL creation is now in its own method.

  * The resource class of factories can be overwritten.

  * The cache timeout value can now be set as a class or instance attribute.

3.5.0a4 (2007-12-28)
====================

- Backed out the changes for the controversial XML-RPC skin support.

3.5.0a3 (2007-11-27)
====================

- make it possible to override menus: this was not possible because new
  interfaces where created any time a menu with the same name was created.

- Resolve ``ZopeSecurityPolicy`` deprecation warning.

3.5.0a2 (2007-08-23)
====================

- <browser:defaultView> now accepts classes as well as interfaces.

3.5.0a1 (2007-08-21)
====================

- Added a `layer` attribute to `xmlrpc:view`. This works just like layers for
  `browser:view` etc. but uses the `IXMLRPCSkinType`.
