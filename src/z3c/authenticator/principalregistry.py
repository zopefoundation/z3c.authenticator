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
"""Principal Registry
"""
import persistent
import zope.interface
from zope.authentication.interfaces import PrincipalLookupError
from zope.container import contained
from zope.principalregistry.principalregistry import principalRegistry
from zope.schema.fieldproperty import FieldProperty

from z3c.authenticator import interfaces


@zope.interface.implementer(interfaces.IPrincipalRegistryAuthenticatorPlugin)
class PrincipalRegistryAuthenticatorPlugin(persistent.Persistent,
                                           contained.Contained):
    """Authenticator Plugin for PrincipalREgistry defined principals.

    This allows us to authenticate principals defined in principal registry.
    """

    allowQueryPrincipal = FieldProperty(
        interfaces.IPrincipalRegistryAuthenticatorPlugin[
            'allowQueryPrincipal'])

    def authenticateCredentials(self, credentials):
        """Return principal if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None

        # get the principal from the principal registry and validate
        try:
            p = principalRegistry.getPrincipalByLogin(credentials['login'])
            if p.validate(credentials["password"]):
                return p
        except KeyError:
            return None
        except AttributeError:
            return None

    def queryPrincipal(self, id, default=None):
        # This will force to use a IFoundPrincipal and allows to apply local
        # groups to global defined principals at local site level. You can
        # disable this feature by set the allowQueryPrincipal option to False.
        if self.allowQueryPrincipal:
            try:
                return principalRegistry.getPrincipal(id) or default
            except PrincipalLookupError:
                pass
        return default
