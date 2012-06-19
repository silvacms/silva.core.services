# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import threading
import logging

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


logger = logging.getLogger('silva.core.services')


class CatalogTaskQueueSavepoint(object):
    grok.implements(IDataManagerSavepoint)

    def __init__(self, manager, active, index, unindex, deleted):
        self.active = active
        self.index = index
        self.unindex = unindex
        self.deleted = deleted
        self._manager = manager

    def restore(self):
        self._manager.set_entries(self)


class CatalogTaskQueue(threading.local):
    grok.implements(ISavepointDataManager)

    def __init__(self, manager):
        self.transaction_manager = manager
        self.clear()

    def clear(self):
        self._catalog = None
        self._index = {}
        self._unindex = {}
        self._deleted = {}
        self._active = False
        self._followed = False

    def set_entries(self, status):
        self._active = status.active
        self._index = status.index.copy()
        self._unindex = status.unindex.copy()
        self._deleted = status.deleted.copy()
        if self._active:
            self._follow()

    def _follow(self):
        if not self._followed:
            transaction = self.transaction_manager.get()
            transaction.join(self)
            transaction.addBeforeCommitHook(self.beforeCommit)
            self._followed = True

    def catalog(self):
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
            catalog = self.catalog()
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
            indexes = None
        self._index[path] = [content, indexes]

    def unindex(self, content):
        path = '/'.join(content.getPhysicalPath())
        if not self._active:
            catalog = self.catalog()
            if catalog is not None:
                catalog.uncatalog_object(path)
            else:
                logger.error(u'Cannot unindex content at %s.', path)
            return
        if path in self._index:
            del self._index[path]
        self._unindex[path] = True

    def beforeCommit(self):
        if self._index or self._unindex:
            catalog = self.catalog()
            if catalog is not None:
                for path in self._unindex.keys():
                    catalog.uncatalog_object(path)
                for path, info in self._index.iteritems():
                    attributes = queryAdapter(info[0], ICatalogingAttributes)
                    if attributes is not None:
                        catalog.catalog_object(
                            attributes, uid=path, idxs=info[1])
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
        return CatalogTaskQueueSavepoint(
            self,
            self._active,
            self._index.copy(),
            self._unindex.copy(),
            self._deleted.copy())

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


catalog_queue = CatalogTaskQueue(transaction.manager)


class Cataloging(grok.Adapter):
    """Cataloging support for objects.
    """
    grok.context(Interface)
    grok.provides(ICataloging)
    grok.implements(ICataloging)

    def index(self, indexes=None):
        catalog_queue.index(self.context, indexes)

    def reindex(self, indexes=None):
        catalog_queue.index(self.context, indexes)

    def unindex(self):
        catalog_queue.unindex(self.context)


class RecordStyle(object):
    """Helper class to initialize the catalog lexicon
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


def configure_catalog_service(catalog):
    lexicon_id = 'silva_lexicon'
    # Add lexicon with right splitter (Silva.UnicodeSplitter.Splitter
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



