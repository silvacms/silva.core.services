# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from silva.core.interfaces import ISilvaService


class ICatalogingAttributes(Interface):
    """Represent attributes of a content to catalog.
    """

    def __getattr__(name):
        pass


class ICataloging(Interface):
    """Cataloging support for Silva objects.
    """

    def index(indexes=None):
        """Index the content in the catalog. If a list of indexes
        names is given as argument, only those indexes will be indexed.
        """

    def reindex(indexes=None):
        """Re-index a content in the catalog. If a list of indexes
        names is given as argument, only those indexes will re-indexed.
        """

    def unindex():
        """Un-index a content from the catalog.
        """


class ICatalogService(ISilvaService):
    """Catalog Service, used to catalog content.
    """
