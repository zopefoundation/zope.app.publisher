XML-RPC views
=============

..
  Let's first establish that our management views are around
  so we know that we're running in the right context:

  >>> from zope.app.publisher.testing import AppPublisherLayer
  >>> wsgi_app = AppPublisherLayer.make_wsgi_app()
  >>> print(http(wsgi_app, r"""
  ...   GET /++etc++site/@@SelectedManagementView.html HTTP/1.0
  ...   Authorization: Basic bWdyOm1ncnB3
  ... """))
  HTTP/1.0 302 Moved Temporarily
  Content-Length: 0
  Content-Type: text/plain;charset=utf-8
  Location: @@registration.html

  >>> print(http(wsgi_app, r"""
  ...   GET /@@SelectedManagementView.html HTTP/1.0
  ...   Authorization: Basic bWdyOm1ncnB3
  ... """))
  HTTP/1.0 302 Moved Temporarily
  Content-Length: 0
  Content-Type: text/plain;charset=utf-8
  Location: .

  >>> print(http(wsgi_app, r"""
  ...   GET /++etc++site/manage HTTP/1.1
  ...   Authorization: Basic bWdyOm1ncnB3
  ...
  ... """, handle_errors=False))
  Traceback (most recent call last):
  zope.security.interfaces.Unauthorized: ...

XML-RPC Methods
---------------

There are two ways to write XML-RPC views. You can write views that
provide "methods" for other objects, and you can write views that have
their own methods.  Let's look at the former case first, since it's a
little bit simpler.

Let's write a view that returns a folder listing:

  >>> class FolderListing:
  ...     def contents(self):
  ...         return list(self.context.keys())

Now we'll register it as a view:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...   <include package="zope.security" />
  ...   <xmlrpc:view
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="contents"
  ...       class="zope.app.publisher.xmlrpc.README.FolderListing"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Now, we'll add some items to the root folder:

  >>> print(http(wsgi_app, r"""
  ... POST /@@contents.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 73
  ... Content-Type: application/x-www-form-urlencoded
  ...
  ... type_name=BrowserAdd__zope.site.folder.Folder&new_value=f1"""))
  HTTP/1.1 303 See Other
  ...

  >>> print(http(wsgi_app, r"""
  ... POST /@@contents.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 73
  ... Content-Type: application/x-www-form-urlencoded
  ...
  ... type_name=BrowserAdd__zope.site.folder.Folder&new_value=f2"""))
  HTTP/1.1 303 See Other
  ...

And call our xmlrpc method:

  >>> from zope.app.publisher.xmlrpc.testing import ServerProxy
  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/")
  >>> proxy.contents()
  ['f1', 'f2']

Note that we get an unauthorized error if we don't supply authentication
credentials:

  >>> proxy = ServerProxy(
  ...     wsgi_app, "http://localhost/", handleErrors=False)
  >>> proxy.contents()
  Traceback (most recent call last):
  ...
  zope.security.interfaces.Unauthorized: ...

`ServerProxy` sets an appropriate `Host` header, so applications that serve
multiple virtual hosts can tell the difference:

  >>> class Headers:
  ...     def host(self):
  ...         return self.request.headers.get("Host")

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...   <include package="zope.security" file="meta.zcml" />
  ...
  ...   <class class="zope.app.publisher.xmlrpc.README.Headers">
  ...       <allow attributes="host" />
  ...   </class>
  ...
  ...   <xmlrpc:view
  ...       name="headers"
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="host"
  ...       class="zope.app.publisher.xmlrpc.README.Headers"
  ...       />
  ... </configure>
  ... """)

  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@nonsense.test:81/headers")
  >>> print(proxy.host())
  nonsense.test:81


Named XML-RPC Views
-------------------

Now let's look at views that have their own methods or other
subobjects.  Views that have their own methods have names that appear
in URLs and they get traversed to get to their methods, as in::

   .../somefolder/listing/contents

To make this possible, the view has to support traversal, so that,
when it is traversed, it traverses to its attributes.  To support
traversal, you can implement or provide an adapter to
`zope.publisher.interfaces.IPublishTraverse`. It's actually better to
provide an adapter so that accesses to attributes during traversal are
mediated by the security machinery.  (Object methods are always bound
to unproxied objects, but adapters are bound to proxied objects unless
they are trusted adapters.)

The 'zope.app.publisher.xmlrpc' package provides a base class,
`MethodPublisher`,  that provides the necessary traversal support.  In
particulat, it has an adapter that simply traverses to attributes.

If an XML-RPC view isn't going to be public, then it also has to
implement 'zope.location.ILocation' so that security grants can be
acquired for it, at least with Zope's default security policy. The
`MethodPublisher` class does that too.

Let's modify our view class to use `MethodPublisher`:

  >>> from zope.app.publisher.xmlrpc import MethodPublisher

  >>> class FolderListing(MethodPublisher):
  ...
  ...     def contents(self):
  ...         return list(self.context.keys())

Note that `MethodPublisher` also provides a suitable `__init__`
method, so we don't need one any more.  This time, we'll register it
as as a named view:

  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...
  ...   <xmlrpc:view
  ...       name="listing"
  ...       for="zope.site.folder.IFolder"
  ...       methods="contents"
  ...       class="zope.app.publisher.xmlrpc.README.FolderListing"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Now, when we access the `contents`, we do so through the listing view:

  >>> proxy = ServerProxy(
  ...     wsgi_app, "http://mgr:mgrpw@localhost/listing/")
  >>> proxy.contents()
  ['f1', 'f2']
  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/")
  >>> proxy.listing.contents()
  ['f1', 'f2']

as before, we will get an error if we don't supply credentials:

  >>> proxy = ServerProxy(
  ...     wsgi_app, "http://localhost/listing/", handleErrors=False)
  >>> proxy.contents()
  Traceback (most recent call last):
  ...
  zope.security.interfaces.Unauthorized: ...

Parameters
----------

Of course, XML-RPC views can take parameters, too:

  >>> class ParameterDemo:
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...
  ...     def add(self, first, second):
  ...         return first + second

Now we'll register it as a view:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...
  ...   <xmlrpc:view
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="add"
  ...       class="zope.app.publisher.xmlrpc.README.ParameterDemo"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Then we can issue a remote procedure call with a parameter and get
back, surprise!, the sum:

  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/")
  >>> proxy.add(20, 22)
  42

Faults
------

If you need to raise an error, the preferred way to do it is via an
`xmlrpc.client.Fault`:

  >>> import xmlrpc.client

  >>> class FaultDemo:
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...
  ...     def your_fault(self):
  ...         return xmlrpc.client.Fault(42, u"It's your fault \N{SNOWMAN}!")

Now we'll register it as a view:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...
  ...   <xmlrpc:view
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="your_fault"
  ...       class="zope.app.publisher.xmlrpc.README.FaultDemo"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Now, when we call it, we get a proper XML-RPC fault:

  >>> from xmlrpc.client import Fault
  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/")
  >>> proxy.your_fault()
  Traceback (most recent call last):
  xmlrpc.client.Fault: <Fault 42: "It's your fault ☃!">

DateTime values
---------------

Unfortunately, `xmlrpc.client` does not support Python's
`datetime.datetime` class (it should be made to, really).  DateTime
values need to be encoded as `xmlrpc.client.DateTime` instances:


  >>> class DateTimeDemo:
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...
  ...     def epoch(self):
  ...         return xmlrpc.client.DateTime("19700101T01:00:01")

Now we'll register it as a view:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...
  ...   <xmlrpc:view
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="epoch"
  ...       class="zope.app.publisher.xmlrpc.README.DateTimeDemo"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Now, when we call it, we get a DateTime value

  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/")
  >>> proxy.epoch()
  <DateTime u'19700101T01:00:01' at ...>

Protecting XML/RPC views with class-based permissions
-----------------------------------------------------

When setting up an XML/RPC view with no permission, the permission check is
deferred to the class that provides the view's implementation:

  >>> class ProtectedView(object):
  ...     def public(self):
  ...         return u'foo'
  ...     def protected(self):
  ...         return u'bar'

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...   <include package="zope.security" file="meta.zcml" />
  ...
  ...   <class class="zope.app.publisher.xmlrpc.README.ProtectedView">
  ...       <require permission="zope.ManageContent"
  ...           attributes="protected" />
  ...       <allow attributes="public" />
  ...   </class>
  ...
  ...   <xmlrpc:view
  ...       name="index"
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="public protected"
  ...       class="zope.app.publisher.xmlrpc.README.ProtectedView"
  ...       />
  ... </configure>
  ... """)

An unauthenticated user can access the public method, but not the protected
one:

  >>> proxy = ServerProxy(
  ...     wsgi_app, "http://usr:usrpw@localhost/index", handleErrors=False)
  >>> proxy.public()
  'foo'
  >>> proxy.protected() # doctest: +NORMALIZE_WHITESPACE
  Traceback (most recent call last):
  zope.security.interfaces.Unauthorized: (<zope.app.publisher.xmlrpc.metaconfigure.ProtectedView object at 0x...>, 'protected', 'zope.ManageContent')

As a manager, we can access both:

  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/index")
  >>> proxy.public()
  'foo'
  >>> proxy.protected()
  'bar'

Handling errors with the ServerProxy
------------------------------------

Normal exceptions
+++++++++++++++++

Our server proxy for functional testing also supports getting the original
errors from Zope by not handling the errors in the publisher:


  >>> class ExceptionDemo:
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...
  ...     def your_exception(self):
  ...         raise Exception("Something went wrong!")

Now we'll register it as a view:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...
  ...   <xmlrpc:view
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="your_exception"
  ...       class="zope.app.publisher.xmlrpc.README.ExceptionDemo"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Now, when we call it, we get an XML-RPC fault:

  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/")
  >>> proxy.your_exception()
  Traceback (most recent call last):
  xmlrpc.client.Fault: <Fault -1: 'Unexpected Zope exception: Exception: Something went wrong!'>

We can also give the parameter `handleErrors` to have the errors not be
handled:

  >>> proxy = ServerProxy(
  ...     wsgi_app, "http://mgr:mgrpw@localhost/", handleErrors=False)
  >>> proxy.your_exception()
  Traceback (most recent call last):
  Exception: Something went wrong!

Custom exception handlers
+++++++++++++++++++++++++

Custom exception handlers might lead to status codes != 200.
They are handled as ProtocolError:

  >>> import zope.security.interfaces
  >>> class ExceptionHandlingDemo:
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...
  ...     def your_runtimeerror(self):
  ...         raise RuntimeError('BadLuck!')

  >>> class ExceptionHandlingDemoHandler:
  ...    def __init__(self, context, request):
  ...        self.context = context
  ...        self.request = request
  ...
  ...    def __call__(self):
  ...        self.request.unauthorized('basic realm="Zope"')
  ...        return ''

Now we'll register it as a view:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:browser="http://namespaces.zope.org/browser"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.component" file="meta.zcml" />
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...   <include package="zope.app.publisher.browser" file="meta.zcml" />
  ...
  ...   <view
  ...       for="RuntimeError"
  ...       type="zope.publisher.interfaces.http.IHTTPRequest"
  ...       name="index.html"
  ...       permission="zope.Public"
  ...       factory="zope.app.publisher.xmlrpc.README.ExceptionHandlingDemoHandler"
  ...       />
  ...
  ...   <browser:defaultView
  ...       for="RuntimeError"
  ...       layer="zope.publisher.interfaces.http.IHTTPRequest"
  ...       name="index.html"
  ...       />
  ...
  ...   <xmlrpc:view
  ...       for="zope.site.interfaces.IFolder"
  ...       methods="your_runtimeerror"
  ...       class="zope.app.publisher.xmlrpc.README.ExceptionHandlingDemo"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Now, when we call it, we get an XML-RPC ProtocolError:

  >>> proxy = ServerProxy(wsgi_app, "http://mgr:mgrpw@localhost/")
  >>> proxy.your_runtimeerror()
  Traceback (most recent call last):
  xmlrpc.client.ProtocolError: <ProtocolError for localhost/: 401 401 Unauthorized>

We can also give the parameter `handleErrors` to have the errors not be
handled:

  >>> proxy = ServerProxy(
  ...     wsgi_app, "http://mgr:mgrpw@localhost/", handleErrors=False)
  >>> proxy.your_runtimeerror()
  Traceback (most recent call last):
  RuntimeError: BadLuck!
