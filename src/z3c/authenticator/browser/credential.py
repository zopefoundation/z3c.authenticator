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
"""Credential Forms.
"""
from z3c.form import field
from z3c.formui import form

from z3c.authenticator import interfaces
from z3c.authenticator.interfaces import _


class SessionCredentialsPluginEditForm(form.EditForm):
    """Group edit form."""

    label = _('Edit SessionCredentialsPlugin.')

    fields = field.Fields(interfaces.ISessionCredentialsPlugin).select(
        'loginpagename', 'loginfield', 'passwordfield')


class HTTPBasicAuthCredentialsPluginEditForm(form.EditForm):
    """Group edit form."""

    label = _('Edit HTTPBasicAuthCredentialsPlugin.')

    fields = field.Fields(interfaces.IHTTPBasicAuthCredentialsPlugin).select(
        'realm')
