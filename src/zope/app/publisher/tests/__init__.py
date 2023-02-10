#  Unit tests for zope.app.publisher.


class LoginLogout:
    # Dummy implementation of zope.app.security.browser.auth.LoginLogout

    def __call__(self):
        return None
