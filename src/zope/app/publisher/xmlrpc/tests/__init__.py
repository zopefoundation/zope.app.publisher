try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib

try:
    import httplib
except ImportError:
    import http.client as httplib

from io import BytesIO

from zope.app.publisher.testing import AppPublisherLayer
from zope.app.wsgi.testlayer import http as _http

class FakeSocket(object):

    def __init__(self, data):
        self.data = data

    def makefile(self, mode, bufsize=None):
        assert 'b' in mode
        data = self.data
        if not isinstance(data, bytes):
            data = data.encode('iso-8859-1')
        return BytesIO(data)

def http(query_str, *args, **kwargs):
    wsgi_app = AppPublisherLayer.make_wsgi_app()
    # Strip leading \n
    query_str = query_str.lstrip()
    kwargs.setdefault('handle_errors', True)
    if not isinstance(query_str, bytes):
        query_str = query_str.encode("utf-8")
    return _http(wsgi_app, query_str, *args, **kwargs)


class ZopeTestTransport(xmlrpclib.Transport):
    """xmlrpclib transport that delegates to
    zope.app.wsgi.testlayer.http
    It can be used like a normal transport, including support for basic
    authentication.
    """

    verbose = False
    handleErrors = True

    def request(self, host, handler, request_body, verbose=0):
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: text/xml\n"

        host, extra_headers, _x509 = self.get_host_info(host)
        if extra_headers:
            request += "Authorization: %s\n" % (
                dict(extra_headers)["Authorization"],)

        request += "\n"
        if isinstance(request_body, bytes) and str is not bytes:
            # Python 3
            request = request.encode("ascii")
        request += request_body
        response = http(request, handle_errors=self.handleErrors)

        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        assert errcode == 200

        content = 'HTTP/1.0 ' + errmsg + '\n\n' + response.getBody()

        res = httplib.HTTPResponse(FakeSocket(content))
        res.begin()
        return self.parse_response(res)

def ServerProxy(uri, transport=None, encoding=None,
                verbose=0, allow_none=0, handleErrors=True):
    """A factory that creates a server proxy using the ZopeTestTransport
    by default.
    """
    if transport is None:
        transport = ZopeTestTransport()
    if isinstance(transport, ZopeTestTransport):
        transport.handleErrors = handleErrors
    return xmlrpclib.ServerProxy(uri, transport, encoding, verbose, allow_none)
