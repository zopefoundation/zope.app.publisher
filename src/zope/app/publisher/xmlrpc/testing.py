try:
    import xmlrpclib
except ImportError:  # PY3
    import xmlrpc.client as xmlrpclib

try:
    import httplib
except ImportError:  # PY3
    import http.client as httplib

from io import BytesIO

from zope.app.wsgi.testlayer import http as _http


class FakeSocket(object):

    def __init__(self, data):
        self.data = data

    def makefile(self, mode, bufsize=None):
        assert 'b' in mode
        data = self.data
        assert isinstance(data, bytes)
        return BytesIO(data)


def http(wsgi_app, query_str, *args, **kwargs):
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
        response = http(
            self.wsgi_app, request, handle_errors=self.handleErrors)

        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers)

        body = response.getBody()
        body = body if isinstance(body, bytes) else body.encode('latin-1')
        errmsg = (errmsg
                  if isinstance(errmsg, bytes)
                  else errmsg.encode('ascii'))  # HTTP response lines are ASCII
        content = b'HTTP/1.0 ' + errmsg + b'\n\n' + body

        res = httplib.HTTPResponse(FakeSocket(content))
        res.begin()
        return self.parse_response(res)


def ServerProxy(wsgi_app, uri, transport=None, encoding=None,
                verbose=0, allow_none=0, handleErrors=True,
                **transport_options):
    """A factory that creates a server proxy.

    If ``transport`` is ``None`` use the ``ZopeTestTransport``, it gets
    initialized with ``**transport_options``. Which options are supported
    depends on the used Python version, see
    ``xmlrpc.client.Transport.__init__`` resp. ``xmlrpclib.Transport.__init__``
    for details.
    """
    if transport is None:
        transport = ZopeTestTransport(**transport_options)
        transport.wsgi_app = wsgi_app
    if isinstance(transport, ZopeTestTransport):
        transport.handleErrors = handleErrors
    return xmlrpclib.ServerProxy(uri, transport, encoding, verbose, allow_none)
