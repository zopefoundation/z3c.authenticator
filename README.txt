This package provides an IAuthentication implementation for Zope3. Note that
this implementation is independent of zope.app.authentication and it doesn't
depend on that package. This means it doesn't even use the credential or
authentication plugins offered from zope.app.authentication package.
I only recommend using this package if you need to implement own authentication
concepts and you don't like to use zope.app.authentication as dependency.
