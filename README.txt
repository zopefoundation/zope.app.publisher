========
Overview
========

``zope.publisher`` is a general purpose object publishing framework
which delegates to a publication object for determining the
to-be-published object.  With Zope 3's default publication from
``zope.app.publication``, this is usually a view or a resource.

This package, ``zope.app.publisher``, provides base implementations
for those.  It also provides ZCML directives for configuring views and
resources.  More specifically, ``zope.app.publisher`` defines the
following ZCML directives:

* browser:page

* browser:pages

* browser:view

* browser:menu

* browser:menuItem

* browser:menuItems

* browser:addMenuitem

* browser:resource

* browser:resourceDirectory

* browser:defeaultSkin

* browser:icon

* xmlrpc:view
