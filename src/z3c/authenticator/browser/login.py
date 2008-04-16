##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: login.py 357 2007-03-15 17:17:37Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.publisher.browser import BrowserPage
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import ILogout

from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IWidgets
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from z3c.i18n import MessageFactory as _
from z3c.authenticator import interfaces


class LoginForm(form.Form):
    """Login form."""

    template = getPageTemplate()
    layout = getLayoutTemplate()

    fields = field.Fields(interfaces.ILoginSchema)
    nextURL = None
    prefix = ''

    def getCameFrom(self):
        camefrom = self.request.get('camefrom', None)
        if camefrom is None:
            site = hooks.getSite()
            camefrom = '%s/index.html' % absoluteURL(site, self.request)
        return camefrom

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.prefix = ''
        self.widgets.ignoreContext = True
        self.widgets.ignoreReadonly = True
        self.widgets.update()
        self.widgets['camefrom'].mode = HIDDEN_MODE
        self.widgets['camefrom'].value = self.getCameFrom()

    @property
    def message(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return _(u'Please provide Login Information')
        return u''

    @button.buttonAndHandler(_('Log-in'))
    def handleLogin(self, action):
        """Handle the subscribe action will register and login a user."""
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            data, errors = self.widgets.extract()
            self.nextURL = data['camefrom']

    def __call__(self):
        self.update()
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return ""
        else:
            return self.layout()


class SiteLogout(BrowserPage):

    def __call__(self):
        """Force logout and avoid to hang around the login form."""
        auth = zope.component.getUtility(IAuthentication)
        ILogout(auth).logout(self.request)
        siteURL = absoluteURL(hooks.getSite(), self.request)
        self.request.response.redirect(siteURL + '/loginForm.html')
