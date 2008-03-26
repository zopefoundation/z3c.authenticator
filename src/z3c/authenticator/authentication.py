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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.event
from zope.schema.interfaces import ISourceQueriables
from zope.location.interfaces import ILocation

from zope.app.component import queryNextUtility
from zope.app.container import btree
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import PrincipalLookupError

from z3c.authenticator import interfaces
from z3c.authenticator import event


class Authenticator(btree.BTreeContainer):
    """See z3c.authentication.interfaces.IAuthenticator."""

    zope.interface.implements(IAuthentication, 
        interfaces.IAuthenticator, ISourceQueriables)

    authenticatorPlugins = ()
    credentialsPlugins = ()

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
            queriable = zope.component.queryMultiAdapter((authplugin, self),
                interfaces.IQueriableAuthenticator)
            if queriable is not None:
                yield name, queriable

    def unauthenticatedPrincipal(self):
        return None

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



