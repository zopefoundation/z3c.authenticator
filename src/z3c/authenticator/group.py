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
from zope.interface import alsoProvides
from zope.security.interfaces import IGroup
from zope.security.interfaces import IGroupAwarePrincipal
from zope.security.interfaces import IMemberAwareGroup

from zope.app.container import btree
from zope.app.container import contained
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IAuthenticatedGroup
from zope.app.security.interfaces import IEveryoneGroup
from zope.app import zapi

from z3c.authenticator import interfaces
from z3c.authenticator import event


class Group(persistent.Persistent, contained.Contained):
    """An implementation of IGroup used by the group container."""

    zope.interface.implements(interfaces.IGroup)

    _principals = ()

    def __init__(self, title=u'', description=u''):
        self.title = title
        self.description = description

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
                nocycles(new, [], zapi.principals().getPrincipal)
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


class GroupPrincipal(object):

    zope.interface.implements(interfaces.IGroupPrincipal)
    zope.component.adapts(interfaces.IGroup)

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

    @apply
    def members():
        def get(self):
            return self._group.principals
        def set(self, value):
            self._group.principals = value
        return property(get, set)

    def getUsers(self):
        return self._group.principals

    def setUsers(self, value):
        self._group.principals = value

    def __repr__(self):
        return "<%s %s>" %(self.__class__.__name__, self.id)


class GroupCycle(Exception):
    """There is a cyclic relationship among groups."""

class InvalidPrincipalIds(Exception):
    """A user has a group id for a group that can't be found
    """

class InvalidGroupId(Exception):
    """A user has a group id for a group that can't be found
    """

def nocycles(pids, seen, getPrincipal):
    for pid in pids:
        if pid in seen:
            raise GroupCycle(pid, seen)
        seen.append(pid)
        principal = getPrincipal(pid)
        nocycles(principal.groups, seen, getPrincipal)
        seen.pop()


def specialGroups(event):
    principal = event.principal
    if (IGroup.providedBy(principal) or
        not IGroupAwarePrincipal.providedBy(principal)):
        return

    everyone = zope.component.queryUtility(IEveryoneGroup)
    if everyone is not None:
        principal.groups.append(everyone.id)

    auth = zope.component.queryUtility(IAuthenticatedGroup)
    if auth is not None:
        principal.groups.append(auth.id)


def setGroupsForPrincipal(event):
    """Set group information when a principal is created"""

    principal = event.principal
    if not IGroupAwarePrincipal.providedBy(principal):
        return

    authentication = event.authentication

    for name, plugin in authentication.getAuthenticatorPlugins():
        if not interfaces.IGroupContainer.providedBy(plugin):
            continue
        principal.groups.extend(
            [id for id in plugin.getGroupsForPrincipal(principal.id)])
