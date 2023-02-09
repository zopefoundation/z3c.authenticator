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
"""Interfaces
"""
import zope.deprecation
import zope.interface
import zope.schema
import zope.security.interfaces
from zope.authentication.interfaces import ILogout
from zope.authentication.principal import PrincipalSource
from zope.container.constraints import containers
from zope.container.constraints import contains
from zope.container.interfaces import IContainer
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('z3c')


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


class IPrincipalRegistryAuthenticatorPlugin(IAuthenticatorPlugin):
    """Principal registry authenticator plugin.

    This plugin is a little bit special since principals get returned from
    a IAuthentication source next to the root then any other IAuthenticator.

    By defaut this utility returns global principals and the IAuthenticator
    forces to wrap then within a IFoundPrincipal. This allows us to apply
    local groups to gloal defined principals.

    You can trun of this feature by set allowQueryPrincipal to False.
    Anyway, this is just an optional plugin, you don't have to use it.
    """

    allowQueryPrincipal = zope.schema.Bool(
        title=_('Allow query principal'),
        description=_('Allow query principal. This is useful if an '
                      'authenticator plugin manages principals for another '
                      'authenticator.'),
        default=True,
    )


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


class ISearchable(zope.interface.Interface):
    """An interface for searching using schema-constrained input."""

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


class IAuthenticator(ILogout, IContainer):
    """Authentication utility.

    The Authenticator supports NOT IAuthenticatorPlugin plugins defined
    in zope.app.authentication.interfaces. Because they use and return a
    IPrincipalInfo object in the authenticateCredentials method.

    Note: you have to write your own authenticator plugins because we do not
    use the IPrincipalInfo implementation in this authentication module.
    """

    contains(IPlugin)

    includeNextUtilityForAuthenticate = zope.schema.Bool(
        title=_('Include next utility for authenticate'),
        description=_('Include next utility for authenticate'),
        default=True,
    )

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
        # TODO: The password manager name may get changed if the password get
        #       changed!
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
        default='')


class ISourceSearchCriteria(zope.interface.Interface):
    """Search Interface for this Principal Provider"""

    search = zope.schema.TextLine(
        title=_("Search String"),
        description=_("A Search String"),
        required=False,
        default='',
        missing_value='')


class IUserContainer(IContainer, IAuthenticatorPlugin, ISearchable):
    """Principal container."""

    contains(IUser)

    def add(user):
        """Add a user and returns a the assigned token (principal id)."""

    def getUserByLogin(login):
        """Return the User object by looking it up by it's login"""


# principal interfaces
class IFoundPrincipal(zope.security.interfaces.IGroupClosureAwarePrincipal):
    """Provides found principal returned by IAuthenticator.getPrincipal.

    The only goal of this adapter is to provide a none persistent object which
    we can apply our group of group ids at runtime.

    This is needed because there is no way to keep the group of group info
    in sync if we whould store them in a IGroup implementation as persistent
    information.

    A found principal gets also created by the IAuthenticators search method
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


class IAuthenticatedPrincipal(
        zope.security.interfaces.IGroupClosureAwarePrincipal):
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
class IGroup(zope.security.interfaces.IGroup):
    """IGroup provides the zope.security.interfaces.IGroup.

    This let us use such IGroups as local registered IEveryoneGroup or
    IAuthenticatedGroup utilities.

    Note zope.security.interfaces.IGroup implementations are used for store
    IPrincipal ids of other IPrincipal or IGroup objects.

    zope.security.interfaces.IGroup implemenations are not used for store
    group of group informations. Group of gorup information are collected
    at runtime by the IAuthentication.getPrincipal method via an adapter
    called IFoundPrincipal. I really hope this is understandable.
    """

    containers('z3c.authenticato.interfaces.IGroupContainer')

    id = zope.schema.TextLine(
        title=_("Id"),
        description=_("The unique identification of the principal."),
        required=True,
        readonly=True)

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Provides a title for the permission."),
        required=True)

    description = zope.schema.Text(
        title=_("Description"),
        description=_("Provides a description for the permission."),
        required=False)

    principals = zope.schema.List(
        title=_('Group Principals'),
        description=_("List of ids of principals which belong to the group"),
        value_type=zope.schema.Choice(
            title=_('Group Principals'),
            description=_('Group Principals'),
            source=PrincipalSource()),
        required=False)


class IGroupContainer(IContainer, IAuthenticatorPlugin, ISearchable):

    contains(IGroup)

    prefix = zope.schema.TextLine(
        title=_('Prefix'),
        description=_("Prefix added to IDs of groups in this container"),
        default='',
        required=True,
        readonly=True,
    )

    def getGroupsForPrincipal(principalid):
        """Get groups the given principal belongs to"""

    def getPrincipalsForGroup(groupid):
        """Get principals which belong to the group"""


class IFoundGroup(IFoundPrincipal, zope.security.interfaces.IGroup):
    """IFoundGroup acts as a IFoundPrincipal representing a group.

    This group principal is used as IFoundPrincipal adapter which we adhoc
    apply our inherited groups incouding groups of groups. See IFoundPrincipal
    for more information.

    This means both interface z3c.authenticator.interfaces.IGroupPrincipal and
    z3c.authenticator.interfaces.IGroup provide
    zope.security.interfaces.IGroup.
    """

#    members = zope.interface.Attribute('an iterable of members of the group')


# TODO: deprecate and remove later
IGroupPrincipal = IFoundGroup
zope.deprecation.deprecated(
    'IGroupPrincipal',
    'The IGroupPrincipal interface get replaced by IFoundGroup')


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


class IUnauthenticatedPrincipalCreated(IPrincipalCreated):
    """A unauthenticated principal has been created."""


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
        title='Realm',
        description='HTTP Basic Authentication Realm',
        required=True,
        default='ZAM')


class ISessionCredentials(zope.interface.Interface):
    """ Interface for storing and accessing credentials in a session.

        We use a real class with interface here to prevent unauthorized
        access to the credentials.
    """

    def getLogin():
        """Return login name."""

    def getPassword():
        """Return password."""


class IBrowserFormChallenger(zope.interface.Interface):
    """A challenger that uses a browser form to collect user credentials."""

    prefixes = zope.schema.List(
        title='Form prefixes',
        description='List of prefixes used in different login forms',
        value_type=zope.schema.TextLine(
            title='Form prefix',
            description='Form prefix',
            missing_value='',
            required=True),
        default=[])

    loginpagename = zope.schema.TextLine(
        title='Loginpagename',
        description="""Name of the login form used by challenger.

        The form must provide 'login' and 'password' input fields.
        """,
        default='loginForm.html')

    loginfield = zope.schema.TextLine(
        title='Loginfield',
        description=(
            "Field of the login page in which is looked for the login user"
            " name."),
        default="login")

    passwordfield = zope.schema.TextLine(
        title='Passwordfield',
        description=(
            "Field of the login page in which is looked for the password."),
        default="password")


class IHTTPBasicAuthCredentialsPlugin(ICredentialsPlugin, IHTTPBasicAuthRealm):
    """BAsic authentication credential plugin."""


class ISessionCredentialsPlugin(ICredentialsPlugin, IBrowserFormChallenger):
    """Session credential plugin."""


class ILoginSchema(zope.interface.Interface):
    """The subscription form."""

    login = zope.schema.TextLine(
        title=_('Login'),
        description=_('Your login name.'),
        required=True)

    password = zope.schema.Password(
        title=_('Password'),
        description=_('Your password.'))


# queriable search interfaces
class IQueriableAuthenticator(ISearchable):
    """Indicates the authenticator provides a search UI for principals."""
