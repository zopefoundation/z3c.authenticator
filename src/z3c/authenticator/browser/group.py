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
import zope.event
import zope.lifecycleevent
from zope.traversing.browser import absoluteURL
import zope.schema

from z3c.i18n import MessageFactory as _
from z3c.authenticator import interfaces
from z3c.authenticator import group
from z3c.authenticator import user
from z3c.authenticator.widget import getSourceInputWidget
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.configurator import configurator



class IAddName(zope.interface.Interface):
    """Object name."""

    __name__ = zope.schema.TextLine( 
        title=u'Object Name',
        description=u'Object Name',
        required=True)


# IGroupContainer
class GroupContainerAddForm(form.AddForm):
    """GroupContainer add form."""

    label = _('Add Group Container.')

    fields = field.Fields(IAddName)
    fields += field.Fields(interfaces.IGroupContainer).select(
        'prefix')

    def createAndAdd(self, data):
        obj = group.GroupContainer()
        obj.prefix = data.get('prefix', u'')
        self.contentName = data.get('__name__', u'')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.context[self.contentName] = obj

        #configure
        configurator.configure(obj, data)
        return obj

    def nextURL(self):
        obj = self.context[self.contentName]
        return '%s/index.html' % absoluteURL(obj, self.request)


# IGroup
class GroupAddForm(form.AddForm):
    """Group add form."""

    label = _('Add Group.')

    fields = field.Fields(IAddName)
    fields += field.Fields(interfaces.IGroup).select('title', 'description')

    def createAndAdd(self, data):
        title = data.get('title', u'')
        description = data.get('description', u'')
        obj = group.Group(title, description)
        name = data.get('__name__', u'')
        prefix = self.context.prefix
        if not name.startswith(prefix):
            name = prefix + name
        self.contentName = name
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.context[self.contentName] = obj

        #configure
        configurator.configure(obj, data)
        return obj

    def nextURL(self):
        obj = self.context[self.contentName]
        return '%s/index.html' % absoluteURL(obj, self.request)


class GroupEditForm(form.EditForm):
    """Group edit form."""

    label = _('Edit Group.')
    groupCycleErrorMessage = _('There is a cyclic relationship among groups.')

    fields = field.Fields(interfaces.IGroup).select('title', 'description',
        'principals')

    fields['principals'].widgetFactory = getSourceInputWidget

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        try:
            changes = self.applyChanges(data)
        except group.GroupCycle, e:
            self.status = self.groupCycleErrorMessage
            return
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage