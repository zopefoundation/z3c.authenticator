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
"""User Forms
"""
import zope.event
import zope.interface
import zope.lifecycleevent
import zope.schema
from z3c.form import field
from z3c.formui import form
from zope.traversing.browser import absoluteURL

from z3c.authenticator import interfaces
from z3c.authenticator import user


# Make z3c.configurator optional.
try:
    from z3c.configurator import configurator
except ImportError:
    configurator = None

from z3c.authenticator.interfaces import _


class IAddName(zope.interface.Interface):
    """Object name."""

    __name__ = zope.schema.TextLine(
        title='Object Name',
        description='Object Name',
        required=True)


# IUserContainer
class UserContainerAddForm(form.AddForm):
    """UserContainer add form."""

    label = _('Add User Container.')
    contentName = None

    fields = field.Fields(IAddName)

    def createAndAdd(self, data):
        obj = user.UserContainer()
        self.contentName = data.get('__name__', '')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.context[self.contentName] = obj

        # configure
        if configurator is not None:
            configurator.configure(obj, data)
        return obj

    def nextURL(self):
        obj = self.context[self.contentName]
        return '%s/index.html' % absoluteURL(obj, self.request)


# IUser
class UserAddForm(form.AddForm):
    """User add form."""

    label = _('Add User.')

    fields = field.Fields(interfaces.IUser).select(
        'login',
        'password',
        'title',
        'description',
        'passwordManagerName')

    def createAndAdd(self, data):
        login = data.get('login', '')
        password = data.get('password', '')
        title = data.get('title', '')
        description = data.get('description', '')
        passwordManagerName = data.get('passwordManagerName', '')
        obj = user.User(login, password, title, description,
                        passwordManagerName)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.contentName, usr = self.context.add(obj)

        # configure
        if configurator is not None:
            configurator.configure(obj, data)
        return obj

    def nextURL(self):
        obj = self.context[self.contentName]
        return '%s/index.html' % absoluteURL(obj, self.request)


class UserEditForm(form.EditForm):
    """Group edit form."""

    label = _('Edit User.')

    fields = field.Fields(
        interfaces.IUser).select(
        'login',
        'password',
        'title',
        'description',
        'passwordManagerName')
