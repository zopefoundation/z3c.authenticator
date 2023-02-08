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
"""Users
"""
import random
import socket
import time
from hashlib import md5

import persistent
import zope.component
import zope.interface
from zope.container import btree
from zope.container import contained
from zope.container.interfaces import DuplicateIDError
from zope.password.interfaces import IPasswordManager

from z3c.authenticator import interfaces


# get the IP address only once
try:
    ip = socket.getaddrinfo(socket.gethostname(), 0)[-1][-1][0]
except BaseException:
    ip = '127.0.0.1'


def generateUserIDToken(id):
    """Generates a unique user id token."""
    t = int(time.time() * 1000)
    r = int(random.random() * 100000000000000000)
    data = "{} {} {} {}".format(ip, t, r, id)
    return md5(data.encode('utf-8')).hexdigest()


@zope.interface.implementer(interfaces.IUser)
class User(persistent.Persistent, contained.Contained):
    """User stored in IUserContainer."""

    def __init__(self, login, password, title, description='',
                 passwordManagerName="Plain Text"):
        self._login = login
        self._passwordManagerName = passwordManagerName
        self.password = password
        self.title = title
        self.description = description

    def getPasswordManagerName(self):
        return self._passwordManagerName

    passwordManagerName = property(getPasswordManagerName)

    def _getPasswordManager(self):
        return zope.component.getUtility(IPasswordManager,
                                         self.passwordManagerName)

    def getPassword(self):
        return self._password

    def setPassword(self, password, passwordManagerName=None):
        if passwordManagerName is not None:
            self._passwordManagerName = passwordManagerName
        passwordManager = self._getPasswordManager()
        self._password = passwordManager.encodePassword(password)

    password = property(getPassword, setPassword)

    def checkPassword(self, password):
        passwordManager = self._getPasswordManager()
        return passwordManager.checkPassword(self.password, password)

    def getLogin(self):
        return self._login

    def setLogin(self, login):
        oldLogin = self._login
        self._login = login
        if self.__parent__ is not None:
            try:
                self.__parent__.notifyLoginChanged(oldLogin, self)
            except ValueError:
                self._login = oldLogin
                raise

    login = property(getLogin, setLogin)


@zope.interface.implementer(interfaces.IUserContainer)
class UserContainer(btree.BTreeContainer):
    """A Persistent User Container and authenticator plugin.

    See principalfolder.txt for details.
    """

    def __init__(self):
        super().__init__()
        self.__id_by_login = self._newContainerData()

    def notifyLoginChanged(self, oldLogin, principal):
        """Notify the Container about changed login of a principal.

        We need this, so that our second tree can be kept up-to-date.
        """
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError('Principal Login already taken!')

        del self.__id_by_login[oldLogin]
        self.__id_by_login[principal.login] = principal.__name__

    def __setitem__(self, id, user):
        """Add a IPrincipal object within a correct id.

        Create a UserContainer

        >>> mc = UserContainer()

        Try to add something not providing IUser
        >>> try:
        ...     mc.__setitem__(u'max', object())
        ... except Exception as e:
        ...     print(e)
        Item does not support IUser!

        Create a user with no __name__, this should be added via the add
        method

        >>> user = User(u'max', u'passwd', u'sir')
        >>> try:
        ...     mc.__setitem__(u'max', user)
        ... except Exception as e:
        ...     print(e)
        There is no user id token given!

        Probably we do have a __name__ during copy/paste, so we have to check
        if we get a __parent__ as well

        >>> user = User(u'usertoken', u'passwd', u'sir')
        >>> user.__name__ = u'usertoken'
        >>> user.__parent__ = u'parent'
        >>> try:
        ...     mc.__setitem__(u'usertoken', user)
        ... except Exception as e:
        ...     print(e)
        Paste a object is not supported!

        Try to use a user with no login:

        >>> user = User(u'', u'passwd', u'sir')
        >>> user.__name__ = u''
        >>> try:
        ...     mc.__setitem__(u'', user)
        ... except Exception as e:
        ...     print(e)
        User does not provide a login value!

        Add a login attr since __setitem__ is in need of one

        >>> user = User(u'max', u'passwd', u'sir')
        >>> user.__name__ = u'max'
        >>> mc.__setitem__(u'max', user)

        Now try to use the same login:

        >>> user2 = User(u'max', u'passwd', u'sir')
        >>> user2.__name__ = u'max'
        >>> try:
        ...     mc.__setitem__(u'max', user2)
        ... except Exception as e:
        ...     print(e)
        'Login already taken!'
        """

        # check if we store correct implementations
        if not interfaces.IUser.providedBy(user):
            raise TypeError('Item does not support IUser!')

        # check if there is a user id given
        if user.__name__ != id:
            raise ValueError('There is no user id token given!')

        # check if there is a user id given in we store correct implementations
        if user.__parent__ is not None:
            raise ValueError('Paste a object is not supported!')

        # The user doesn't provide a login
        if not user.login:
            raise ValueError('User does not provide a login value!')

        # A user with the new login already exists
        if user.login in self.__id_by_login:
            raise DuplicateIDError('Login already taken!')

        super().__setitem__(id, user)
        self.__id_by_login[user.login] = id

    def add(self, user):
        token = generateUserIDToken(user.login)
        # Pre set the user id like a ticket, so we can check it in __setitem__
        user.__name__ = token
        self[token] = user
        return token, self[token]

    def __delitem__(self, id):
        """Remove principal information."""
        user = self[id]
        super().__delitem__(id)
        del self.__id_by_login[user.login]

    def authenticateCredentials(self, credentials):
        """Return principal if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        id = self.__id_by_login.get(credentials['login'])
        if id is None:
            return None
        user = self[id]
        if not user.checkPassword(credentials["password"]):
            return None
        return user

    def getUserByLogin(self, login):
        # don't bother catching KeyError, it's the task of the caller
        return self[self.__id_by_login[login]]

    def queryPrincipal(self, id, default=None):
        user = self.get(id)
        if user is not None:
            return user
        return default

    def search(self, query, start=None, batch_size=None):
        """Search through this principal provider."""
        search = query.get('search')
        if search is None:
            return
        search = search.lower()
        n = 1
        for i, value in enumerate(self.values()):
            if (search in value.title.lower() or
                search in value.description.lower() or
                    search in value.login.lower()):
                if not ((start is not None and i < start)
                        or (batch_size is not None and n > batch_size)):
                    n += 1
                    yield value.__name__
