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
"""Vocabularies
"""

import base64

import zope.component
import zope.dublincore.interfaces
import zope.i18n
import zope.interface
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory

from z3c.authenticator import interfaces
from z3c.authenticator.interfaces import _


UTILITY_TITLE = _(
    'z3c.authenticator.vocabulary-utility-plugin-title',
    '${name} (a utility)')
CONTAINED_TITLE = _(
    'z3c.authenticator.vocabulary-contained-plugin-title',
    '${name} (in contents)')
MISSING_TITLE = _(
    'z3c.authenticator.vocabulary-missing-plugin-title',
    '${name} (not found; deselecting will remove)')


def mktok(s):
    tok = base64.encodebytes(s.encode('utf-8')).decode('utf-8')
    return tok.strip()


def _pluginVocabulary(context, interface, attr_name):
    """Vocabulary that provides names of plugins of a specified interface.

    Given an interface, the options should include the unique names of all of
    the plugins that provide the specified interface for the current context--
    which is expected to be a pluggable authentication utility, hereafter
    referred to as a Authenticator).

    These plugins may be objects contained within the Authenticator
    ("contained plugins"), or may be utilities registered for the specified
    interface, found in the context of the Authenticator
    ("utility plugins"). Contained plugins mask utility plugins of the same
    name.

    The vocabulary also includes the current values of the
    Authenticator even if they do not correspond to a contained or
    utility plugin.
    """
    terms = {}
    auth = interfaces.IAuthenticator.providedBy(context)
    if auth:
        for k, v in context.items():
            if interface.providedBy(v):
                dc = zope.dublincore.interfaces.IDCDescriptiveProperties(
                    v, None)
                if dc is not None and dc.title:
                    title = dc.title
                else:
                    title = k
                terms[k] = vocabulary.SimpleTerm(
                    k, mktok(k), zope.i18n.Message(
                        CONTAINED_TITLE, mapping={'name': title}))
    utils = zope.component.getUtilitiesFor(interface, context)
    for nm, util in utils:
        if nm not in terms:
            terms[nm] = vocabulary.SimpleTerm(
                nm, mktok(nm), zope.i18n.Message(
                    UTILITY_TITLE, mapping={'name': nm}))
    if auth:
        for nm in set(getattr(context, attr_name)):
            if nm not in terms:
                terms[nm] = vocabulary.SimpleTerm(
                    nm, mktok(nm), zope.i18n.Message(
                        MISSING_TITLE, mapping={'name': nm}))
    return vocabulary.SimpleVocabulary(
        [term for nm, term in sorted(terms.items())])


def authenticatorPlugins(context):
    return _pluginVocabulary(
        context, interfaces.IAuthenticatorPlugin, 'authenticatorPlugins')


zope.interface.alsoProvides(authenticatorPlugins, IVocabularyFactory)


def credentialsPlugins(context):
    return _pluginVocabulary(
        context, interfaces.ICredentialsPlugin, 'credentialsPlugins')


zope.interface.alsoProvides(credentialsPlugins, IVocabularyFactory)
