# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.app.container.interfaces import IObjectAddedEvent
from five import grok

from OFS.interfaces import IObjectWillBeRemovedEvent
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.Silva.helpers import add_and_edit, \
    register_service, unregister_service

from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf
from silva.core.services.interfaces import ICatalogService


class CatalogService(ZCatalog, SilvaService):
    """The Service catalog.
    """

    meta_type = "Silva Service Catalog"

    grok.implements(ICatalogService)
    silvaconf.factory('manage_addCatalogService')


def manage_addCatalogService(self, id, title=None, REQUEST=None):
    """Add a catalog service.
    """

    service = CatalogService(id, title)
    register_service(self, id, service, ICatalogService)
    add_and_edit(self, id, REQUEST)
    return ''


@grok.subscribe(ICatalogService, IObjectWillBeRemovedEvent)
def unregisterCatalogTool(service, event):
    unregister_service(service, ICatalogService)


class RecordStyle(object):
    """Helper class to initialize the catalog lexicon
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


@grok.subscribe(ICatalogService, IObjectAddedEvent)
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
                ]
            )

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
        ('version_status', 'FieldIndex'),
        ('haunted_path', 'FieldIndex'),]

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
