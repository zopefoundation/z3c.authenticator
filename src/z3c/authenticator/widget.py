##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Principal Source Widget Implementation
"""
import zope.component
import zope.i18n
import zope.interface
import zope.schema
import zope.schema.interfaces
from z3c.form import button
from z3c.form import converter
from z3c.form import field
from z3c.form.browser import text
from z3c.form.browser import widget
from z3c.form.i18n import MessageFactory as _
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ISequenceWidget
from z3c.form.interfaces import ITerms
from z3c.form.widget import FieldWidget
from z3c.form.widget import SequenceWidget
from z3c.formui import form
from z3c.template.template import getLayoutTemplate
from zope.authentication.interfaces import IAuthentication
from zope.authentication.interfaces import IPrincipalSource
from zope.traversing import api

from z3c.authenticator import interfaces


class IPrincipalSourceWidget(IFieldWidget):
    """SourceWidget."""

    def addValue(value):
        """Add and render value as sequence item."""


class ISourceResultWidget(ISequenceWidget):
    """Search form result widget."""

    def addValue(value):
        """Add and render value as sequence item."""


class ISourceSearchForm(zope.interface.Interface):
    """Search schema."""


# TODO: remove this if we have a fixed version of z3c.form
class PrincipalSourceDataConverter(converter.CollectionSequenceDataConverter):
    """A special converter between collections and sequence widgets."""

    zope.component.adapts(zope.schema.interfaces.IList, IPrincipalSourceWidget)

    def toWidgetValue(self, value):
        widget = self.widget
        if widget.terms is None:
            widget.updateTerms()
        return [widget.terms.getTerm(entry).token for entry in value]

    def toFieldValue(self, value):
        widget = self.widget
        # bugfix, avoid to call lenght on terms
        # if not widget.terms:
        if widget.terms is None:
            widget.updateTerms()
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        return collectionType([widget.terms.getValue(token)
                               for token in value])


# TODO: remove this if we have a fixed version of z3c.form
class SourceSearchDataConverter(converter.CollectionSequenceDataConverter):
    """A special converter between collections and sequence widgets."""

    zope.component.adapts(zope.schema.interfaces.IList, ISourceResultWidget)

    def toWidgetValue(self, value):
        widget = self.widget
        if widget.terms is None:
            widget.updateTerms()
        return [widget.terms.getTerm(entry).token for entry in value]

    def toFieldValue(self, value):
        widget = self.widget
        # bugfix, avoid to call lenght on terms
        # if not widget.terms:
        if widget.terms is None:
            widget.updateTerms()
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        return collectionType([widget.terms.getValue(token)
                               for token in value])


class PrincipalTerm:

    def __init__(self, token, title):
        self.token = token
        self.title = title


@zope.interface.implementer(ITerms)
@zope.component.adapter(
    zope.interface.Interface,
    IFormLayer,
    zope.interface.Interface,
    zope.schema.interfaces.IList,
    IPrincipalSourceWidget)
class PrincipalTerms:

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.source = field.value_type.bind(self.context).vocabulary

    def getTerm(self, pid):
        if pid not in self.source:
            raise LookupError(pid)

        auth = zope.component.getUtility(IAuthentication)
        principal = auth.getPrincipal(pid)

        if principal is None:
            raise LookupError(pid)

        return PrincipalTerm(pid.encode('base64').strip().replace('=', '_'),
                             principal.title)

    def getTermByToken(self, token):
        pid = token.replace('_', '=').decode('base64')
        return self.getTerm(pid)

    def getValue(self, token):
        return token.replace('_', '=').decode('base64')

    def __contains__(self, pid):
        if pid in self.source:
            return True
        return False

    def __iter__(self):
        raise NotImplementedError('Source queriable is not iterable.')

    def __len__(self):
        raise NotImplementedError('Source queriable does not provide lenght.')


class ISearchFormResultsField(zope.schema.interfaces.IList):
    """Search form results field.

    Marker for the right widget.
    """


@zope.interface.implementer(ISearchFormResultsField)
class SearchFormResultsField(zope.schema.List):
    """Search form results field."""


@zope.interface.implementer(ISourceResultWidget)
class SourceResultWidget(widget.HTMLInputWidget, SequenceWidget):
    """Knows how to catch the right terms."""

    klass = 'search-form-widget checkbox-widget'
    searchResults = []
    value = []
    items = []

    def isChecked(self, term):
        return term.token in self.value

    def addValue(self, value):
        term = self.terms.getTerm(value)
        checked = self.isChecked(term)
        label = zope.i18n.translate(term.title, context=self.request,
                                    default=term.title)
        id = '{}-{}'.format(self.id, term.token)
        item = {'id': id, 'name': self.name + ':list', 'value': term.token,
                'label': label, 'checked': checked}
        if item not in self.items:
            self.items.append(item)

    def updateTerms(self):
        self.terms = self.form.terms
        return self.terms

    def extract(self, default=[]):
        """See z3c.form.interfaces.IWidget."""
        tokens = super().extract(default)
        for value in self.searchResults:
            token = self.terms.getTerm(value).token
            if token not in tokens:
                tokens.append(token)
        return tokens

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super().update()
        widget.addFieldClass(self)

        # update search forms
        self.items = []

        # append existing items
        for token in self.value:
            value = self.terms.getValue(token)
            self.addValue(value)


def getSourceResultWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return FieldWidget(field, SourceResultWidget(request))


class SourceSearchWidget(text.TextWidget):
    """Source search widget."""

    style = 'border-color: gray; width:100px;'

    @property
    def label(self):
        txt = _('search in: ')
        prefix = zope.i18n.translate(txt, context=self.request, default=txt)
        return '{}{}'.format(prefix, self.form.title)

    @label.setter
    def label(self, value):
        pass


def getSourceSearchWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, SourceSearchWidget(request))


class ISearchResult(zope.interface.Interface):
    """Search value."""

    results = SearchFormResultsField(
        title=_('Principals'),
        description=_("Principal ids"),
        default=[],
        required=False
    )

# conditions


def hasResults(form):
    return bool(form.widgets['search'].value)


@zope.interface.implementer(ISourceSearchForm)
class SearchFormMixin(form.Form):
    """Source Query View search form."""

    layout = getLayoutTemplate('subform')

    formErrorsMessage = _('Search error')
    ignoreContext = True
    terms = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def title(self):
        if hasattr(self.context, 'title'):
            return self.context.title
        return api.getName(self.context)

    def search(self, data):
        raise NotImplementedError('Subform must implement search')

    @button.buttonAndHandler(_('Search'))
    def handleSearch(self, action):
        """Set search result"""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        value = self.search(data)
        self.widgets['results'].searchResults = value
        self.widgets['results'].update()

    @button.buttonAndHandler(_('Add'), condition=hasResults)
    def handleAdd(self, action):
        """Set search result"""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        for value in data.get('results', []):
            self.__parent__.addValue(value)


class AuthenticatorSearchForm(SearchFormMixin):
    """Source search form for ISourceSearchCriteria."""

    fields = field.Fields(interfaces.ISourceSearchCriteria).select('search')
    fields += field.Fields(ISearchResult)

    fields['results'].widgetFactory = getSourceResultWidget
    fields['search'].widgetFactory = getSourceSearchWidget

    def search(self, data):
        # avoid empty search strings
        value = []
        if data.get('search'):
            value = self.context.search(data) or []
        return value


class PrincipalRegistrySearchForm(SearchFormMixin):
    """Source Query View search form for global PrincipalRegistry."""

    fields = field.Fields(interfaces.ISourceSearchCriteria).select('search')
    fields += field.Fields(ISearchResult)

    fields['results'].widgetFactory = getSourceResultWidget
    fields['search'].widgetFactory = getSourceSearchWidget

    @property
    def title(self):
        return 'principals.zcml'

    def search(self, data):
        # avoid empty search strings
        if data.get('search'):
            searchStr = data.get('search')
            value = [principal.id
                     for principal in self.context.getPrincipals(searchStr)]
        return value


@zope.interface.implementer_only(IPrincipalSourceWidget)
@zope.component.adapter(zope.interface.Interface,
                        IPrincipalSource, zope.interface.Interface)
class PrincipalSourceWidget(widget.HTMLInputWidget, SequenceWidget):
    """Select widget implementation."""

    klass = 'principal-source-widget checkbox-widget'
    value = []
    items = []

    def __init__(self, field, source, request):
        self.field = field
        self.source = source
        self.request = request

    def isChecked(self, term):
        return term.token in self.value

    def addValue(self, value):
        term = self.terms.getTerm(value)
        checked = self.isChecked(term)
        label = zope.i18n.translate(term.title, context=self.request,
                                    default=term.title)
        id = '{}-{}'.format(self.id, term.token)
        item = {'id': id, 'name': self.name + ':list', 'value': term.token,
                'label': label, 'checked': checked}
        if item not in self.items:
            self.items.append(item)

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super().update()
        widget.addFieldClass(self)

        # update serach forms
        self.items = []
        self.updateSearchForms()

        # append existing items
        for token in self.value:
            value = self.terms.getValue(token)
            self.addValue(value)

    def updateSearchForms(self):
        queriables = zope.schema.interfaces.ISourceQueriables(
            self.source, None)
        if queriables is None:
            # treat the source itself as a queriable
            queriables = ((self.name + '.query', self.source), )
        else:
            queriables = [
                (self.name + '.' +
                 str(i).encode('base64').strip().replace('=', '_'),
                 s)
                for (i, s) in queriables.getQueriables()]

        self.searchForms = []
        append = self.searchForms.append
        for (name, source) in queriables:
            searchForm = zope.component.getMultiAdapter((source, self.request),
                                                        ISourceSearchForm)
            # ignore views which do not follow the update/render pattern
            if hasattr(searchForm, 'update'):
                searchForm.prefix = name
                searchForm.__parent__ = self
                searchForm.__name__ = name
                # set the same terms for this form
                searchForm.terms = self.terms
                searchForm.update()
                append(searchForm)

    def getSearchForms(self):
        return self.searchForms


def getSourceInputWidget(field, request):
    """Sequence IFieldWidget factory for ISource."""
    source = field.value_type.vocabulary
    widget = zope.component.getMultiAdapter((field, source, request),
                                            IFieldWidget)
    return widget
