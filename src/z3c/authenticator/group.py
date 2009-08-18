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

import BTrees.OOBTree
import persistent

import zope.interface
import zope.component
import zope.event
import zope.deprecation
import zope.deferredimport

from zope.interface import alsoProvides
from zope.security.interfaces import IGroup
from zope.security.interfaces import IGroupAwarePrincipal

from zope.app.container import btree
from zope.app.container import contained
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IAuthenticatedGroup
from zope.app.security.interfaces import IEveryoneGroup
from zope.app.security.interfaces import IUnauthenticatedGroup
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from z3c.authenticator import interfaces
from z3c.authenticator import event

zope.deferredimport.deprecated(
    "FoundPrincipal has moved to z3c.authenticator.group.FoundGroup",
    FoundPrincipal = 'z3c.authenticator.principal:FoundGroup',
    )


class Group(persistent.Persistent, contained.Contained):
    """An implementation of IGroup used by the group container."""

    zope.interface.implements(interfaces.IGroup)

    _principals = ()

    def __init__(self, title=u'', description=u''):
        self.title = title
        self.description = description

    @property
    def id(self):
        """The id is the name which includes the container prefix (readonly)."""
        return self.__name__

    def setPrincipals(self, prinlist, check=True):
        # method is not a part of the interface
        parent = self.__parent__
        old = self._principals
        self._principals = tuple(prinlist)

        oldset = set(old)
        new = set(prinlist)
        gid = self.__name__
        removed = oldset - new
        added = new - oldset
        try:
            parent._removePrincipalsFromGroup(removed, gid)
        except AttributeError:
            removed = None

        try:
            parent._addPrincipalsToGroup(added, gid)
        except AttributeError:
            added = None

        if check:
            try:
                auth = zope.component.getUtility(IAuthentication)
                nocycles(new, [], auth.getPrincipal)
            except GroupCycle:
                # abort
                self.setPrincipals(old, False)
                raise
        # now that we've gotten past the checks, fire the events.
        if removed:
            zope.event.notify(
                event.PrincipalsRemovedFromGroup(removed, gid))
        if added:
            zope.event.notify(
                event.PrincipalsAddedToGroup(added, gid))

    principals = property(lambda self: self._principals, setPrincipals)

    def __repr__(self):
        return "<%s %s>" %(self.__class__.__name__, self.__name__)


class GroupContainer(btree.BTreeContainer):

    zope.interface.implements(interfaces.IGroupContainer)

    def __init__(self, prefix=u''):
        self.prefix = prefix
        super(GroupContainer,self).__init__()
        # __inversemapping is used to map principals to groups
        self.__inverseMapping = BTrees.OOBTree.OOBTree()

    def __setitem__(self, name, group):
        """Add a IGroup object within a correct id.

        Create a GroupContainer

        >>> gc = GroupContainer('groups')

        Try to add something not providing IGroup
        >>> try:
        ...     gc.__setitem__(u'groups.members', object())
        ... except Exception, e:
        ...     print e
        Group does not support IGroup!

        Create a group and add them with a wrong prefix:

        >>> group = Group(u'users')
        >>> try:
        ...     gc.__setitem__(u'123', group)
        ... except Exception, e:
        ...     print e
        'Wrong prefix used in group id!'

        Add a login attr since __setitem__ is in need of one

        >>> gc.__setitem__(u'groups.users', group)
        """
        # check if we store correct groups
        if not interfaces.IGroup.providedBy(group):
            raise TypeError('Group does not support IGroup!')

        # check if the given id provides the used prefix
        if not name.startswith(self.prefix):
            raise KeyError('Wrong prefix used in group id!')

        super(GroupContainer, self).__setitem__(name, group)
        gid = group.__name__
        self._addPrincipalsToGroup(group.principals, gid)
        if group.principals:
            zope.event.notify(
                event.PrincipalsAddedToGroup(group.principals, gid))
        zope.event.notify(event.GroupAdded(group))

    def addGroup(self, id, group):
        id = self.prefix + id
        self[id] = group
        return id, self[id]

    def __delitem__(self, gid):
        group = self[gid]
        self._removePrincipalsFromGroup(group.principals, gid)
        if group.principals:
            zope.event.notify(
                event.PrincipalsRemovedFromGroup(group.principals, gid))
        super(GroupContainer, self).__delitem__(gid)

    def _addPrincipalsToGroup(self, pids, gid):
        for pid in pids:
            self.__inverseMapping[pid] = (
                self.__inverseMapping.get(pid, ()) + (gid,))

    def _removePrincipalsFromGroup(self, pids, gid):
        for pid in pids:
            groups = self.__inverseMapping.get(pid)
            if groups is None:
                return
            new = tuple([id for id in groups if id != gid])
            if new:
                self.__inverseMapping[pid] = new
            else:
                del self.__inverseMapping[pid]

    def getGroupsForPrincipal(self, pid):
        """Get groups the given principal belongs to"""
        return self.__inverseMapping.get(pid, ())

    def getPrincipalsForGroup(self, gid):
        """Get principals which belong to the group"""
        return self[gid].principals

    def search(self, query, start=None, batch_size=None):
        """ Search for groups"""
        search = query.get('search')
        if search is not None:
            n = 0
            search = search.lower()
            for i, (id, groupinfo) in enumerate(self.items()):
                if (search in groupinfo.title.lower() or
                    (groupinfo.description and 
                     search in groupinfo.description.lower())):
                    if not ((start is not None and i < start) or
                            (batch_size is not None and n >= batch_size)):
                        n += 1
                        yield id

    def authenticateCredentials(self, credentials):
        # group container don't authenticate
        pass

    def queryPrincipal(self, id, default=None):
        return self.get(id, default)


class GroupCycle(Exception):
    """There is a cyclic relationship among groups."""


def nocycles(pids, seen, getPrincipal):
    for pid in pids:
        if pid in seen:
            raise GroupCycle(pid, seen)
        seen.append(pid)
        principal = getPrincipal(pid)
        # not every principal has groups and there is no consistent marker
        # interface for mark group aware. See IUnauthenticatedPrincipal
        groups = getattr(principal, 'groups', ())
        nocycles(groups, seen, getPrincipal)
        seen.pop()


# specialGroups
@zope.component.adapter(interfaces.IPrincipalCreated)
def specialGroups(event):
    """Set groups for IGroupAwarePrincipal."""

    principal = event.principal
    # only apply to non groups because it will end in cycle dependencies
    # since the principal will have tis role anyway
    if (IGroup.providedBy(principal) or
        not (IGroupAwarePrincipal.providedBy(principal) or
             IUnauthenticatedPrincipal.providedBy(principal))):
        return

    # global utility registered by everybodyGroup directive
    everyone = zope.component.queryUtility(IEveryoneGroup)
    if everyone is not None and everyone.id != principal.id and \
        everyone.id not in principal.groups:
        principal.groups.append(everyone.id)

    if IUnauthenticatedPrincipal.providedBy(principal):
        # global utility registered by unauthenticatedGroup directive
        unAuthGroup = zope.component.queryUtility(IUnauthenticatedGroup)
        if unAuthGroup is not None and unAuthGroup.id != principal.id and \
            unAuthGroup.id not in principal.groups:
            principal.groups.append(unAuthGroup.id)
    else:
        # global utility registered by authenticatedGroup directive
        authGroup = zope.component.queryUtility(IAuthenticatedGroup)
        if authGroup is not None and authGroup.id != principal.id and \
            authGroup.id not in principal.groups:
            principal.groups.append(authGroup.id)


@zope.component.adapter(interfaces.IPrincipalCreated)
def setGroupsForPrincipal(event):
    """Set local group information when a principal is created.
    
    Note: IUnauthenticatedPrincipal does not provide IGroupAwarePrincipal which
    is just wrong and makes the conditions a little bit complicated.
    """

    principal = event.principal
    # set only groups for group aware principals or unauthenticated which are
    # group aware too. This allows us to apply local roles to unautenticated
    # principals which allows to apply permissions/roles via local groups which
    # the application does not provide at global level.
    if not (IGroupAwarePrincipal.providedBy(principal) or
            IUnauthenticatedPrincipal.providedBy(principal)):
        return

    authentication = event.authentication
    for name, plugin in authentication.getAuthenticatorPlugins():
        if not interfaces.IGroupContainer.providedBy(plugin):
            continue
        # set groups for principals but not a group to itself. This could happen
        # for global defined groups
        principal.groups.extend(
            [id for id in plugin.getGroupsForPrincipal(principal.id)
             if id != principal.id])
