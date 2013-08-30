# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
import collections

from five import grok
from zope.interface import Interface
from zope.component import queryAdapter, queryUtility

from Products.ZCatalog.ZCatalog import ZCatalog

from silva.core import conf as silvaconf
from silva.core.services.base import SilvaService, get_service_id
from silva.core.services.interfaces import ICatalogService
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes
from silva.core.services.delayed import Task, lazy
from silva.core.interfaces import IUpgradeTransaction

logger = logging.getLogger('silva.core.services')

CatalogTodo = collections.namedtuple(
    'CatalogTodo', ['content', 'indexes', 'initial'])


class CatalogingTask(Task):
    priority = 1000

    def __init__(self, active=False, index=None, unindex=None):
        self._active = active
        self._index = {} if index is None else index.copy()
        self._unindex = {} if unindex is None else unindex.copy()

    def copy(self):
        return CatalogingTask(self._active, self._index, self._unindex)

    @lazy
    def catalog(self):
        return queryUtility(ICatalogService)

    def activate(self):
        if not self._active:
            self._active = True

    def index(self, content, indexes=None):
        path = '/'.join(content.getPhysicalPath())
        if not self._active:
            if self.catalog is not None:
                attributes = queryAdapter(content, ICatalogingAttributes)
                if attributes is not None:
                    self.catalog.catalog_object(
                        attributes,
                        uid=path,
                        idxs=indexes)
                    return
            logger.error(u'Cannot index content at %s.', path)
            return
        existing = path in self._unindex
        if existing:
            del self._unindex[path]
        current = self._index.get(path)
        if current is not None:
            task = CatalogTodo(content, None, current.initial)
        else:
            # If the content existed in the unindex query, when it is
            # not initial.
            task = CatalogTodo(content, indexes, not existing)
        self._index[path] = task

    def reindex(self, content, indexes=None):
        path = '/'.join(content.getPhysicalPath())
        if not self._active:
            if self.catalog is not None:
                attributes = queryAdapter(content, ICatalogingAttributes)
                if attributes is not None:
                    self.catalog.catalog_object(
                        attributes,
                        uid=path,
                        idxs=indexes)
                    return
            logger.error(u'Cannot index content at %s.', path)
            return
        if path in self._unindex:
            del self._unindex[path]
        current = self._index.get(path)
        if current is not None:
            task = CatalogTodo(content, None, current.initial)
        else:
            # This content is not initial.
            task = CatalogTodo(content, indexes, False)
        self._index[path] = task

    def unindex(self, content):
        path = '/'.join(content.getPhysicalPath())
        if not self._active:
            if self.catalog is not None:
                self.catalog.uncatalog_object(path)
                return
            logger.error(u'Cannot unindex content at %s.', path)
            return
        current = self._index.get(path)
        if current is not None:
            del self._index[path]
            if current.initial:
                # The content was scheduled to be catalog initialy,
                # but have been removed since.
                return
        self._unindex[path] = True

    def finish(self):
        if self._index or self._unindex:
            if self.catalog is not None:
                for path in self._unindex.keys():
                    self.catalog.uncatalog_object(path)
                for path, info in self._index.iteritems():
                    attributes = queryAdapter(
                        info.content, ICatalogingAttributes)
                    if attributes is not None:
                        self.catalog.catalog_object(
                            attributes, uid=path, idxs=info.indexes)
            else:
                logger.error(
                    u'Could not get catalog to catalog content '
                    u'in the transaction.')


@grok.subscribe(IUpgradeTransaction)
def activate_upgrade(event):
    CatalogingTask.get().activate()


class Cataloging(grok.Adapter):
    """Cataloging support for objects.
    """
    grok.context(Interface)
    grok.provides(ICataloging)
    grok.implements(ICataloging)

    def index(self, indexes=None):
        CatalogingTask.get().index(self.context, indexes)

    def reindex(self, indexes=None):
        CatalogingTask.get().reindex(self.context, indexes)

    def unindex(self):
        CatalogingTask.get().unindex(self.context)


class RecordStyle(object):
    """Helper class to initialize the catalog lexicon
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


def configure_catalog_service(catalog):
    lexicon_id = 'silva_lexicon'
    # Add lexicon with right splitter (silva.core.service.splitter.Splitter
    # registers under "Unicode Whitespace splitter")
    if not lexicon_id in catalog.objectIds():
        # XXX ugh, hardcoded dependency on names in ZCTextIndex
        catalog.manage_addProduct['ZCTextIndex'].manage_addLexicon(
            lexicon_id,
            elements=[
                RecordStyle(
                    group='Case Normalizer', name='Case Normalizer'),
                RecordStyle(
                    group='Stop Words', name=" Don't remove stop words"),
                RecordStyle(
                    group='Word Splitter', name="Unicode Whitespace splitter"),
                ])

    existing_columns = catalog.schema()
    columns = ['id',
               'content_intid',
               'publication_status',
               'meta_type',]

    for column_name in columns:
        if column_name in existing_columns:
            continue
        catalog.addColumn(column_name)

    existing_indexes = catalog.indexes()
    indexes = [
        ('id', 'FieldIndex'),
        ('meta_type', 'FieldIndex'),
        ('path', 'PathIndex'),
        ('fulltext', 'ZCTextIndex'),
        ('publication_status', 'FieldIndex')]

    for field_name, field_type in indexes:
        if field_name in existing_indexes:
            continue

        # special handling for argument passing to zctextindex ranking
        # algorithm used is best for larger text body / query size
        # ratios
        if field_type == 'ZCTextIndex':
            extra = RecordStyle(
                doc_attr=field_name,
                lexicon_id='silva_lexicon',
                index_type='Okapi BM25 Rank')
            catalog.addIndex(field_name, field_type, extra)
            continue

        catalog.addIndex(field_name, field_type)


class CatalogService(ZCatalog, SilvaService):
    """The Service catalog.
    """
    meta_type = "Silva Service Catalog"
    grok.implements(ICatalogService)
    grok.name('service_catalog')
    silvaconf.default_service(setup=configure_catalog_service)

    # XXX Fix reindex
    def __init__(self, id=None, title=None, *args, **kw):
        # Compatibility with SilvaService factory
        super(CatalogService, self).__init__(
            get_service_id(self, id), title or self.meta_type, *args, **kw)



