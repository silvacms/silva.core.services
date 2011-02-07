# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.interface import Interface
from zope import component

from Products.ZCatalog.ZCatalog import ZCatalog

from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ICatalogService
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes


class Cataloging(grok.Adapter):
    """Cataloging support for objects.
    """
    grok.context(Interface)
    grok.provides(ICataloging)
    grok.implements(ICataloging)

    def __init__(self, context):
        super(Cataloging, self).__init__(context)
        self._path = '/'.join(self.context.getPhysicalPath())
        self._catalog = component.queryUtility(ICatalogService)

    def index(self, indexes=None):
        # We might not have any catalog to work with
        if self._catalog is None:
            return
        # Get attributes to index
        attributes = component.queryAdapter(self.context, ICatalogingAttributes)
        if attributes is not None:
            self._catalog.catalog_object(
                attributes, uid=self._path, idxs=indexes)

    def reindex(self, indexes=None):
        # We just need to index again to re-index.
        self.index(indexes=indexes)

    def unindex(self):
        # We might not have any catalog to work with
        if self._catalog is None:
            return
        self._catalog.uncatalog_object(self._path)


class CatalogService(ZCatalog, SilvaService):
    """The Service catalog.
    """
    meta_type = "Silva Service Catalog"
    grok.implements(ICatalogService)

    # XXX Fix reindex
    def __init__(self, id, *args, **kw):
        # compatibility with SilvaService factory
        super(CatalogService, self).__init__(id)


class RecordStyle(object):
    """Helper class to initialize the catalog lexicon
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


@grok.subscribe(ICatalogService, IObjectCreatedEvent)
def configureCatalogService(catalog, event):

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
        ('version_status', 'FieldIndex')]

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
