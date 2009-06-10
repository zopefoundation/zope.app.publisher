========
Overview
========

*This package is at present not reusable without depending on a large
chunk of the Zope Toolkit and its assumptions. It is maintained by the*
`Zope Toolkit project <http://docs.zope.org/zopetoolkit/>`_.

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

* browser:defaultSkin

* browser:icon

* xmlrpc:view


Views and Browser pages
=======================

XXX writeme


Resources
=========

Resources are static files and directories that are served to the browser
directly from the filesystem. The most common example are images, CSS style
sheets, or JavaScript files.

Resources are be registered under a symbolic name and can later be referred to
by that name, so their usage is independent from their physical location.

You can register a single file with the `<browser:resource>` directive, and a
whole directory with the `<browser:resourceDirectory>` directive, for example

  <browser:resource
    directory="/path/to/static.file"
    name="myfile"
    />

  <browser:resourceDirectory
    directory="/path/to/images"
    name="main-images"
    />

This causes a named adapter to be registered that adapts the request to
zope.interface.Interface (XXX why do we not use an explicit interface?),
so to later retrieve a resource, use
`zope.component.getAdapter(request, name='myfile')`.

There are two ways to traverse to a resource,
1. with the 'empty' view on a site, e. g. `http://localhost/@@/myfile`
   (This is declared by zope.app.publisher.browser)
2. with the `++resource++` namespace, e. g. `http://localhost/++resource++myfile`
   (This is declared by zope.traversing.namespace)

In case of resource-directories traversal simply continues through its contents,
e. g. `http://localhost/@@/main-images/subdir/sample.jpg`

Rather than putting together the URL to a resource manually, you should use
zope.traversing.browser.interfaces.IAbsoluteURL to get the URL, or for a
shorthand, call the resource object. This has two additional benefits.

Firstly, if you want to serve resources from a different URL, for example
because you want to use a web server specialized in serving static files instead
of the appserver, you can register an IAbsoluteURL adapter for the site under
the name 'resource' that will be used to compute the base URLs for resources.

For example, if you register 'http://static.example.com/' as the base 'resource'
URL, the resources from the above example would yield the following absolute
URLs: http://static.example.com/myfile and
http://static.example.com/main-images
(XXX what about http://static.example.com/main-images/subdir/sample.jpg?)

The other benefit of using generated URLs is about dealing with browser caches,
as described in the next section.

Browser Caches
~~~~~~~~~~~~~~

While we want browsers to cache static resources such as CSS-stylesheets and
JavaScript files, we also want them *not* to use the cached version if the
files on the server have been updated. (And we don't want to make end-users
have to empty their browser cache to get the latest version. Nor explain how
to do that over the phone every time.)

To make browsers update their caches of resources immediately when the
resource changes, the absolute URLs of resources can now be made to contain a
hash of the resource's contents, so it will look like
/++noop++12345/@@/myresource instead of /@@/myresource.

In developer mode the hash is recomputed each time the resource is asked for
its URL, while in production mode the hash is computed only once, so remember
to restart the server after changing resource files (else browsers will still
see the old URL unchanged and use their outdated cached versions of the files).

This feature is deactivated by default, to activate it, use
<meta:provides feature="zope.app.publisher.hashed-resources" />
