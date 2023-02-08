from zope.deferredimport import deprecated


deprecated(
    "The contents of zope/app/publisher/xmlrpc/tests/__init__.py have been"
    " moved to zope/app/publisher/xmlrpc/testing.py for reusability."
    " Please import from there.",
    FakeSocket='zope.app.publisher.xmlrpc.testing:FakeSocket',
    http='zope.app.publisher.xmlrpc.testing:http',
    ZopeTestTransport='zope.app.publisher.xmlrpc.testing:ZopeTestTransport',
    ServerProxy='zope.app.publisher.xmlrpc.testing:ServerProxy',
)
