# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import threading
import logging
import collections

from five import grok
from zope.interface import Interface
from zope.component import queryAdapter, queryUtility
from transaction.interfaces import ISavepointDataManager, IDataManagerSavepoint
import transaction

from Products.ZCatalog.ZCatalog import ZCatalog

from silva.core import conf as silvaconf
from silva.core.services.base import SilvaService, get_service_id
from silva.core.services.interfaces import ICatalogService
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes
from silva.core.interfaces import IUpgradeTransaction

logger = logging.getLogger('silva.core.services')

CatalogTask = collections.namedtuple(
    'CatalogTask', ['content', 'indexes', 'initial'])


class TaskQueueSavepoint(object):
    grok.implements(IDataManagerSavepoint)

    def __init__(self, manager, active, index, unindex):
        self.active = active
        self.index = index
        self.unindex = unindex
        self._manager = manager

    def restore(self):
        self._manager.set_entries(self)


class TaskQueue(threading.local):
    grok.implements(ISavepointDataManager)

    def __init__(self, manager):
        self.transaction_manager = manager
        self.clear()

    def clear(self):
        self._catalog = None
        self._index = {}
        self._unindex = {}
        self._active = False
        self._followed = False

    def set_entries(self, status):
        self._active = status.active
        self._index = status.index.copy()
        self._unindex = status.unindex.copy()
        if self._active:
            self._follow()

    def _follow(self):
        if not self._followed:
            transaction = self.transaction_manager.get()
            transaction.join(self)
            transaction.addBeforeCommitHook(self.beforeCommit)
            self._followed = True

    def get_catalog(self):
        if self._catalog is None:
            self._catalog = queryUtility(ICatalogService)
            if self._catalog is not None:
                self._follow()
        return self._catalog

    def activate(self):
        if not self._active:
            self._follow()
            self._active = True

    def index(self, content, indexes=None):
        path = '/'.join(content.getPhysicalPath())
        if not self._active:
            catalog = self.get_catalog()
            if catalog is not None:
                attributes = queryAdapter(content, ICatalogingAttributes)
                if attributes is not None:
                    catalog.catalog_object(attributes, uid=path, idxs=indexes)
                    return
            logger.error(u'Cannot index content at %s.', path)
            return
        existing = path in self._unindex
        if existing:
            del self._unindex[path]
        current = self._index.get(path)
        if current is not None:
            task = CatalogTask(content, None, current.initial)
        else:
            # If the content existed in the unindex query, when it is
            # not initial.
            task = CatalogTask(content, indexes, not existing)
        self._index[path] = task

    def reindex(self, content, indexes=None):
        path = '/'.join(content.getPhysicalPath())
        if not self._active:
            catalog = self.get_catalog()
            if catalog is not None:
                attributes = queryAdapter(content, ICatalogingAttributes)
                if attributes is not None:
                    catalog.catalog_object(attributes, uid=path, idxs=indexes)
                    return
            logger.error(u'Cannot index content at %s.', path)
            return
        if path in self._unindex:
            del self._unindex[path]
        current = self._index.get(path)
        if current is not None:
            task = CatalogTask(content, None, current.initial)
        else:
            # This content is not initial.
            task = CatalogTask(content, indexes, False)
        self._index[path] = task

    def unindex(self, content):
        path = '/'.join(content.getPhysicalPath())
        if not self._active:
            catalog = self.get_catalog()
            if catalog is not None:
                catalog.uncatalog_object(path)
            else:
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

    def beforeCommit(self):
        if self._index or self._unindex:
            catalog = self.get_catalog()
            if catalog is not None:
                for path in self._unindex.keys():
                    catalog.uncatalog_object(path)
                for path, info in self._index.iteritems():
                    attributes = queryAdapter(
                        info.content, ICatalogingAttributes)
                    if attributes is not None:
                        catalog.catalog_object(
                            attributes, uid=path, idxs=info.indexes)
            else:
                logger.error(
                    u'Could not get catalog to catalog content '
                    u'in the transaction.')
        self.clear()

    # We have to implement all of this in order to be able to
    # implement abort.

    def sortKey(self):
        return 'A' * 50

    def savepoint(self):
        return TaskQueueSavepoint(
            self,
            self._active,
            self._index.copy(),
            self._unindex.copy())

    def commit(self, transaction):
        pass

    def abort(self, transaction):
        self.clear()

    def tpc_begin(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    def tpc_abort(self, transaction):
        pass


task_queue = TaskQueue(transaction.manager)

@grok.subscribe(IUpgradeTransaction)
def activate_upgrade(event):
    task_queue.activate()


class Cataloging(grok.Adapter):
    """Cataloging support for objects.
    """
    grok.context(Interface)
    grok.provides(ICataloging)
    grok.implements(ICataloging)

    def index(self, indexes=None):
        task_queue.index(self.context, indexes)

    def reindex(self, indexes=None):
        task_queue.reindex(self.context, indexes)

    def unindex(self):
        task_queue.unindex(self.context)


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



