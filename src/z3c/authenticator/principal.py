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
"""Principal
"""
import zope.component
import zope.interface
from zope.authentication.interfaces import IAuthentication
from zope.security.interfaces import IPrincipal

from z3c.authenticator import interfaces


class PrincipalBase:
    """Base class for IAuthenticatedPrincipal and IFoundPrincipal principals.
    """

    title = None

    def __init__(self, principal):
        """We offer no access to the principal object itself."""
        self.id = principal.__name__
        self.title = principal.title
        self.description = principal.description
        self.groups = []

    @property
    def allGroups(self):
        """This method is not used in zope by default, but nice to have it."""
        if self.groups:
            seen = set()
            auth = zope.component.getUtility(IAuthentication)
            stack = [iter(self.groups)]
            while stack:
                try:
                    group_id = next(stack[-1])
                except StopIteration:
                    stack.pop()
                else:
                    if group_id not in seen:
                        yield group_id
                        seen.add(group_id)
                        group = auth.getPrincipal(group_id)
                        stack.append(iter(group.groups))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)


@zope.component.adapter(interfaces.IUser)
@zope.interface.implementer(interfaces.IAuthenticatedPrincipal)
class AuthenticatedPrincipal(PrincipalBase):
    """Default IAuthenticatedPrincipal principal."""


@zope.component.adapter(interfaces.IUser)
@zope.interface.implementer(interfaces.IFoundPrincipal)
class FoundPrincipal(PrincipalBase):
    """Default IFoundPrincipal principal."""


@zope.component.adapter(IPrincipal)
@zope.interface.implementer(interfaces.IAuthenticatedPrincipal)
class AuthenticatedPrincipalForPrincipal(PrincipalBase):
    """IAuthenticatedPrincipal principal for IPrincipal."""


@zope.component.adapter(IPrincipal)
@zope.interface.implementer(interfaces.IFoundPrincipal)
class FoundPrincipalForPrincipal(PrincipalBase):
    """IFoundPrincipal principal for IPrincipal."""


@zope.interface.implementer(interfaces.IFoundGroup)
@zope.component.adapter(zope.security.interfaces.IGroup)
class FoundGroup:

    def __init__(self, group):
        self.id = group.__name__
        self._group = group
        self.groups = []

    @property
    def allGroups(self):
        if self.groups:
            seen = set()
            auth = zope.component.getUtility(IAuthentication)
            stack = [iter(self.groups)]
            while stack:
                try:
                    group_id = stack[-1].next()
                except StopIteration:
                    stack.pop()
                else:
                    if group_id not in seen:
                        yield group_id
                        seen.add(group_id)
                        group = auth.getPrincipal(group_id)
                        stack.append(iter(group.groups))

    @property
    def title(self):
        return self._group.title

    @property
    def description(self):
        return self._group.description

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)
