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


from z3c.i18n import MessageFactory as _
from z3c.authenticator import interfaces
from z3c.formui import form
from z3c.form import field

from z3c.i18n import MessageFactory as _
from z3c.authenticator import interfaces


class AuthenticatorEditForm(form.EditForm):
    """Group edit form."""

    label = _('Edit Authenticator.')

    fields = field.Fields(interfaces.IAuthenticator).select(
        'credentialsPlugins', 'authenticatorPlugins')


class EditGroup(form.EditForm):
    """Group edit form."""

    label = _('Edit Group.')

    form_fields = form.Fields(interfaces.IGroup).select('title', 
        'description', 'principals')
