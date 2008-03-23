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
import zope.schema

from zope.security.interfaces import IGroupClosureAwarePrincipal
from zope.security.interfaces import IMemberAwareGroup
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.container.interfaces import IContainer
from zope.app.container.constraints import contains
from zope.app.container.constraints import containers
from zope.app.security.interfaces import ILogout
from zope.app.security.vocabulary import PrincipalSource

from z3c.i18n import MessageFactory as _


class IPlugin(zope.interface.Interface):
    """A plugin for IAuthenticator component."""


# authenticator interfaces
class IAuthenticatorPlugin(IPlugin):
    """Authenticates and provides a principal using credentials."""

    containers('z3c.authenticator.interfaces.IAuthenticator')

    def authenticateCredentials(credentials):
        """Authenticates credentials and return a IPrincipal object.

        If the credentials can be authenticated, return an object that provides
        IPrincipal. If the plugin cannot authenticate the credentials,
        returns None.
        """

    def queryPrincipal(id, default=None):
        """Returns an IPrincipal object for the given principal id or default.

        If the plugin cannot find information for the id, returns None.
        """


class ICredentialsPlugin(IPlugin):
    """Handles credentials extraction and challenges per request."""

    containers('z3c.authenticator.interfaces.IAuthenticator')

    challengeProtocol = zope.interface.Attribute(
        """A challenge protocol used by the plugin.

        If a credentials plugin works with other credentials pluggins, it
        and the other cooperating plugins should specify a common (non-None)
        protocol. If a plugin returns True from its challenge method, then
        other credentials plugins will be called only if they have the same
        protocol.
        """)

    def extractCredentials(request):
        """Ties to extract credentials from a request.

        A return value of None indicates that no credentials could be found.
        Any other return value is treated as valid credentials.
        """

    def challenge(request):
        """Possibly issues a challenge.

        This is typically done in a protocol-specific way.

        If a challenge was issued, return True, otherwise return False.
        """

    def logout(request):
        """Possibly logout.

        If a logout was performed, return True, otherwise return False.
        """


class IAuthenticator(ILogout, IContainer):
    """Authentication utility.
    
    The Authenticator supports NOT IAuthenticatorPlugin plugins defined 
    in zope.app.authentication.interfaces. Because they use and return a 
    IPrincipalInfo object in the authenticateCredentials method.
    
    Note: you have to write your own authenticator plugins because we do not 
    use the IPrincipalInfo implementation in this authentication module.
    """

    contains(IPlugin)

    credentialsPlugins = zope.schema.List(
        title=_('Credentials Plugins'),
        description=_("""Used for extracting credentials.
        Names may be of ids of non-utility ICredentialsPlugins contained in
        the IAuthenticator, or names of registered
        ICredentialsPlugins utilities.  Contained non-utility ids mask 
        utility names."""),
        value_type=zope.schema.Choice(vocabulary='Z3CCredentialsPlugins'),
        default=[],
        )

    authenticatorPlugins = zope.schema.List(
        title=_('Authenticator Plugins'),
        description=_("""Used for converting credentials to principals.
        Names may be of ids of non-utility IAuthenticatorPlugins contained in
        the IAuthenticator, or names of registered
        IAuthenticatorPlugins utilities.  Contained non-utility ids mask 
        utility names."""),
        value_type=zope.schema.Choice(vocabulary='Z3CAuthenticatorPlugins'),
        default=[],
        )

    def getCredentialsPlugins():
        """Return iterable of (plugin name, actual credentials plugin) pairs.
        Looks up names in credentialsPlugins as contained ids of non-utility
        ICredentialsPlugins first, then as registered ICredentialsPlugin
        utilities.  Names that do not resolve are ignored.
        """

    def getAuthenticatorPlugins():
        """Return iterable of (plugin name, actual authenticator plugin) pairs.
        Looks up names in authenticatorPlugins as contained ids of non-utility
        IAuthenticatorPlugins first, then as registered IAuthenticatorPlugin
        utilities.  Names that do not resolve are ignored.
        """

    def logout(request):
        """Performs a logout by delegating to its authenticator plugins."""



# user interfaces
class IUser(zope.interface.Interface):
    """User"""

    containers('z3c.authenticator.interfaces.IUserContainer')

    login = zope.schema.TextLine(
        title=_("Login"),
        description=_("The Login/Username of the principal. "
                      "This value can change."))

    password = zope.schema.Password(
        title=_("Password"),
        description=_("The password for the principal."))

    passwordManagerName = zope.schema.Choice(
        title=_("Password Manager"),
        vocabulary="Password Manager Names",
        description=_("The password manager will be used"
            " for encode/check the password"),
        default="Plain Text",
        # TODO: The password manager name may be changed only
        # if the password changed
        readonly=True
        )

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Provides a title for the principal."))

    description = zope.schema.Text(
        title=_("Description"),
        description=_("Provides a description for the principal."),
        required=False,
        missing_value='',
        default=u'')


class IUserSearchCriteria(zope.interface.Interface):
    """Search Interface for this Principal Provider"""

    search = zope.schema.TextLine(
        title=_("Search String"),
        description=_("A Search String"),
        required=False,
        default=u'',
        missing_value=u'')


class IUserContainer(IContainer, IAuthenticatorPlugin):
    """Principal container."""

    contains(IUser)


# principal interfaces
class IFoundPrincipal(IGroupClosureAwarePrincipal):
    """A factory adapting IUser and offering read access to the principal.
    
    A found principal gets created by the IAuthenticators search method
    for users matching the search critaria.
    """

    id = zope.interface.Attribute("The principal id.")

    title = zope.interface.Attribute("The principal title.")

    description = zope.interface.Attribute("A description of the principal.")

    groups = zope.schema.List(
        title=_("Groups"),
        description=_(
            """Ids of groups to which the user directly belongs.

            Plugins may append to this list.  Mutating the list only affects
            the life of the principal object, and does not persist (so
            persistently adding groups to a principal should be done by working
            with a plugin that mutates this list every time the principal is
            created, like the group container in this package.)
            """),
        value_type=zope.schema.TextLine(),
        required=False)


class IAuthenticatedPrincipal(IGroupClosureAwarePrincipal):
    """A factory adapting IInternalPrincipal and offering read access to the 
    principal.
    
    A authenticated principal gets created by the IAuthenticators 
    authenticateCredentials method for principals matching the credential 
    criteria.
    """

    id = zope.interface.Attribute("The principal id.")

    title = zope.interface.Attribute("The principal title.")

    description = zope.interface.Attribute("A description of the principal.")

    groups = zope.schema.List(
        title=_("Groups"),
        description=_(
            """Ids of groups to which the user directly belongs.

            Plugins may append to this list.  Mutating the list only affects
            the life of the principal object, and does not persist (so
            persistently adding groups to a principal should be done by working
            with a plugin that mutates this list every time the principal is
            created, like the group container in this package.)
            """),
        value_type=zope.schema.TextLine(),
        required=False)


# group interfaces
class IGroup(zope.interface.Interface):

    containers('z3c.authenticato.interfaces.IGroupContainer')

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Provides a title for the permission."),
        required=True)

    description = zope.schema.Text(
        title=_("Description"),
        description=_("Provides a description for the permission."),
        required=False)

    principals = zope.schema.List(
        title=_("Principals"),
        value_type=zope.schema.Choice(
            source=PrincipalSource()),
        description=_(
        "List of ids of principals which belong to the group"),
        required=False)


class IGroupContainer(IContainer, IAuthenticatorPlugin):

    contains(IGroup)

    prefix = zope.schema.TextLine(
        title=_('Prefix'),
        description=_("Prefix added to IDs of groups in this container"),
        default=u'',
        required=True,
        readonly=True,
        )

    def getGroupsForPrincipal(principalid):
        """Get groups the given principal belongs to"""

    def getPrincipalsForGroup(groupid):
        """Get principals which belong to the group"""


class IGroupSearchCriteria(zope.interface.Interface):

    search = zope.schema.TextLine(
        title=_("Group Search String"),
        required=False,
        missing_value=u'',
        )


class IGroupPrincipal(IFoundPrincipal, IMemberAwareGroup):
    """IGroup that acts as a principal representing a group."""

    members = zope.interface.Attribute('an iterable of members of the group')


# principal event interfaces
class IPrincipalCreated(zope.interface.Interface):
    """A principal has been created."""

    principal = zope.interface.Attribute("The principal that was created")

    authentication = zope.interface.Attribute(
        "The authentication utility that created the principal")


class IAuthenticatedPrincipalCreated(IPrincipalCreated):
    """A principal has been created by way of an authentication operation."""

    request = zope.interface.Attribute(
        "The request the user was authenticated against")


class IFoundPrincipalCreated(IPrincipalCreated):
    """A principal has been created by way of a search operation."""


# group event interfaces
class IGroupAdded(zope.interface.Interface):
    """A group has been added."""

    group = zope.interface.Attribute("""The group that was defined""")


class IPrincipalsAddedToGroup(zope.interface.Interface):
    group_id = zope.interface.Attribute(
        'the id of the group to which the principal was added')
    principal_ids = zope.interface.Attribute(
        'an iterable of one or more ids of principals added')


class IPrincipalsRemovedFromGroup(zope.interface.Interface):

    group_id = zope.interface.Attribute(
        'the id of the group from which the principal was removed')

    principal_ids = zope.interface.Attribute(
        'an iterable of one or more ids of principals removed')


# credential
class IHTTPBasicAuthRealm(zope.interface.Interface):
    """HTTP Basic Auth Realm

    Represents the realm string that is used during basic HTTP authentication
    """

    realm = zope.schema.TextLine(
        title=u'Realm',
        description=u'HTTP Basic Authentication Realm',
        required=True,
        default=u'ZAM')


class ISessionCredentials(zope.interface.Interface):
    """ Interface for storing and accessing credentials in a session.

        We use a real class with interface here to prevent unauthorized
        access to the credentials.
    """

    def __init__(login, password):
        pass

    def getLogin():
        """Return login name."""

    def getPassword():
        """Return password."""


class IBrowserFormChallenger(zope.interface.Interface):
    """A challenger that uses a browser form to collect user credentials."""

    loginpagename = zope.schema.TextLine(
        title=u'Loginpagename',
        description=u"""Name of the login form used by challenger.

        The form must provide 'login' and 'password' input fields.
        """,
        default=u'loginForm.html')

    loginfield = zope.schema.TextLine(
        title=u'Loginfield',
        description=u"Field of the login page in which is looked for the login user name.",
        default=u"login")

    passwordfield = zope.schema.TextLine(
        title=u'Passwordfield',
        description=u"Field of the login page in which is looked for the password.",
        default=u"password")


class IHTTPBasicAuthCredentialsPlugin(ICredentialsPlugin, IHTTPBasicAuthRealm):
    """BAsic authentication credential plugin."""


class ISessionCredentialsPlugin(ICredentialsPlugin, IBrowserFormChallenger):
    """Session credential plugin."""


class ILoginSchema(zope.interface.Interface):
    """The subscription form."""

    login = zope.schema.TextLine(
        title=_(u'Login'),
        description=_(u'Your login name.'),
        required=True)

    password = zope.schema.Password(
        title=_(u'Password'),
        description=_(u'Your password.'))

    camefrom = zope.schema.TextLine(
        title=_(u'Camefrom'),
        description=_(u'The url which the user came form.'))


# queriable search interfaces
class IQueriableAuthenticator(zope.interface.Interface):
    """Indicates the authenticator provides a search UI for principals."""


class IQuerySchemaSearch(zope.interface.Interface):
    """An interface for searching using schema-constrained input."""

    schema = zope.interface.Attribute("""
        The schema that constrains the input provided to the search method.

        A mapping of name/value pairs for each field in this schema is used
        as the query argument in the search method.
        """)

    def search(query, start=None, batch_size=None):
        """Returns an iteration of principal IDs matching the query.

        query is a mapping of name/value pairs for fields specified by the
        schema.

        If the start argument is provided, then it should be an
        integer and the given number of initial items should be
        skipped.

        If the batch_size argument is provided, then it should be an
        integer and no more than the given number of items should be
        returned.
        """

