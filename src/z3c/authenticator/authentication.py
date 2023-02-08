##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Authentication
"""
import zope.component
import zope.event
import zope.interface
from zope.authentication.interfaces import IAuthentication
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.authentication.interfaces import PrincipalLookupError
from zope.component import queryNextUtility
from zope.container import btree
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import ISourceQueriables

from z3c.authenticator import event
from z3c.authenticator import interfaces


@zope.interface.implementer(IAuthentication,
                            interfaces.IAuthenticator, ISourceQueriables)
class Authenticator(btree.BTreeContainer):
    """See z3c.authentication.interfaces.IAuthenticator."""

    authenticatorPlugins = ()
    credentialsPlugins = ()

    includeNextUtilityForAuthenticate = FieldProperty(
        interfaces.IAuthenticator['includeNextUtilityForAuthenticate'])

    def _plugins(self, names, interface):
        for name in names:
            plugin = self.get(name)
            if not interface.providedBy(plugin):
                plugin = zope.component.queryUtility(interface, name,
                                                     context=self)
            if plugin is not None:
                yield name, plugin

    def getAuthenticatorPlugins(self):
        return self._plugins(self.authenticatorPlugins,
                             interfaces.IAuthenticatorPlugin)

    def getCredentialsPlugins(self):
        return self._plugins(self.credentialsPlugins,
                             interfaces.ICredentialsPlugin)

    def authenticate(self, request):
        authenticatorPlugins = [p for n, p in self.getAuthenticatorPlugins()]
        for name, credplugin in self.getCredentialsPlugins():
            credentials = credplugin.extractCredentials(request)
            if credentials is None:
                # do not invoke the auth plugin without credentials
                continue

            for authplugin in authenticatorPlugins:
                if authplugin is None:
                    continue
                principal = authplugin.authenticateCredentials(credentials)
                if principal is None:
                    continue

                # create authenticated principal
                authenticated = interfaces.IAuthenticatedPrincipal(principal)

                # send the IAuthenticatedPrincipalCreated event
                zope.event.notify(event.AuthenticatedPrincipalCreated(
                    self, authenticated, request))
                return authenticated

        if self.includeNextUtilityForAuthenticate:
            next = queryNextUtility(self, IAuthentication)
            if next is not None:
                principal = next.authenticate(request)
                if principal is not None:
                    return principal

        return None

    def getPrincipal(self, id):
        for name, authplugin in self.getAuthenticatorPlugins():
            principal = authplugin.queryPrincipal(id)
            if principal is None:
                continue

            # create found principal
            found = interfaces.IFoundPrincipal(principal)

            # send the IFoundPrincipalCreated event
            zope.event.notify(event.FoundPrincipalCreated(self, found))
            return found

        next = queryNextUtility(self, IAuthentication)
        if next is not None:
            return next.getPrincipal(id)
        raise PrincipalLookupError(id)

    def getQueriables(self):
        for name, authplugin in self.getAuthenticatorPlugins():
            queriable = zope.component.queryMultiAdapter(
                (authplugin, self), interfaces.IQueriableAuthenticator)
            if queriable is not None:
                yield name, queriable

    def unauthenticatedPrincipal(self):
        """Return unauthenticated principal or None.

        This allows you to return an unauthenticated principal. This could be
        usefull if you don't like to fallback to the global unauthenticated
        principal usage. Why is this usefull. The reason is, if a global
        principal get returned, there is no event notification involved like
        we have in IPrincipalCreated which whould allow to apply groups. And
        there is no way to apply local groups to global unauthenticated
        principals it they get returned by the global IAuthentication or the
        fallback implementation. See zope.principalregistry

        Usage:

        Return an unauthenticated principal within this method if you need to
        apply local groups. This allows to apply local groups for the returned
        unauthenticated principal if you use a custom subscriber for
        IPrincipalCreated. Note, the local group must define the global
        unauthenticated principals id in the principals list. Use the zcml
        directive called unauthenticatedPrincipal for define the global
        unauthenticated principal.
        """
        principal = zope.component.queryUtility(IUnauthenticatedPrincipal)
        if principal is not None:
            zope.event.notify(event.UnauthenticatedPrincipalCreated(self,
                                                                    principal))
        return principal

    def unauthorized(self, id, request):
        challengeProtocol = None

        for name, credplugin in self.getCredentialsPlugins():
            protocol = getattr(credplugin, 'challengeProtocol', None)
            if challengeProtocol is None or protocol == challengeProtocol:
                if credplugin.challenge(request):
                    if protocol is None:
                        return
                    elif challengeProtocol is None:
                        challengeProtocol = protocol

        if challengeProtocol is None:
            next = queryNextUtility(self, IAuthentication)
            if next is not None:
                next.unauthorized(id, request)

    def logout(self, request):
        challengeProtocol = None

        for name, credplugin in self.getCredentialsPlugins():
            protocol = getattr(credplugin, 'challengeProtocol', None)
            if challengeProtocol is None or protocol == challengeProtocol:
                if credplugin.logout(request):
                    if protocol is None:
                        return
                    elif challengeProtocol is None:
                        challengeProtocol = protocol

        if challengeProtocol is None:
            next = queryNextUtility(self, IAuthentication)
            if next is not None:
                next.logout(request)


@zope.component.adapter(interfaces.ISearchable, interfaces.IAuthenticator)
@zope.interface.implementer(interfaces.IQueriableAuthenticator, ILocation)
class QueriableAuthenticator:
    """Performs schema-based principal searches adapting ISearchable and
    IAuthenticator.

    Delegates the search to the adapted authenticator which also provides
    ISearchable. See IAuthenticator.getQueriables for more infos.
    """

    def __init__(self, authplugin, pau):
        # locate them
        if ILocation.providedBy(authplugin):
            self.__parent__ = authplugin.__parent__
            self.__name__ = authplugin.__name__
        else:
            self.__parent__ = pau
            self.__name__ = ""
        self.authplugin = authplugin
        self.pau = pau

    def search(self, query, start=None, batch_size=None):
        yield from self.authplugin.search(query, start, batch_size)
