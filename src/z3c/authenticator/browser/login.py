##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
##############################################################################
"""Login Form
"""
import zope.component
from z3c.form import button
from z3c.form import field
from z3c.form.interfaces import IWidgets
from z3c.formui import form
from z3c.template.template import getLayoutTemplate
from z3c.template.template import getPageTemplate
from zope.authentication.interfaces import IAuthentication
from zope.authentication.interfaces import ILogout
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.component import hooks
from zope.publisher.browser import BrowserPage
from zope.session.interfaces import ISession
from zope.traversing.browser import absoluteURL

from z3c.authenticator import interfaces
from z3c.authenticator.interfaces import _


class LoginForm(form.Form):
    """Login form without prefix in form and widget which works with session
    credentail plugin out of the box.
    """

    template = getPageTemplate()
    layout = getLayoutTemplate()

    fields = field.Fields(interfaces.ILoginSchema)
    nextURL = None
    prefix = ''

    @property
    def message(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return _('Please provide Login Information')
        return ''

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        # the session credential use input fields without prefixes
        self.widgets.prefix = ''
        self.widgets.ignoreContext = True
        self.widgets.ignoreReadonly = True
        self.widgets.update()

    @button.buttonAndHandler(_('Log-in'))
    def handleLogin(self, action):
        """Handle the subscribe action will register and login a user."""
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            session = ISession(self.request, None)
            sessionData = session.get('z3c.authenticator.credential.session')
            if sessionData is not None and sessionData.get('camefrom'):
                self.nextURL = sessionData['camefrom']
                sessionData['camefrom'] = None

    def __call__(self):
        self.update()
        if self.nextURL is not None:
            # the redirect method will prevent us to redirect to a 3rd party
            # domains since zope.publisher version 3.9.3
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
