# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Acquisition import aq_base
from OFS import SimpleItem

from five import grok
from five.intid.intid import OFSIntIds
from silva.core import conf as silvaconf
from silva.core import interfaces
from zope.intid.interfaces import IIntIds


class ZMIObject(SimpleItem.SimpleItem):
    grok.baseclass()
    grok.implements(interfaces.IZMIObject)


def get_service_id(service, id):
    if id:
        return id
    id = grok.name.bind().get(service)
    if id:
        return id
    if hasattr(aq_base(service), 'default_service_identifier'):
        return service.default_service_identifier
    return None


class SilvaService(ZMIObject):
    grok.baseclass()
    grok.implements(interfaces.ISilvaService)

    def __init__(self, id=None, title=None):
        self.id = get_service_id(self, id)
        self.title = title or self.meta_type

    def getId(self):
        return get_service_id(self, self.id)


class IntIdService(OFSIntIds, SilvaService):
    grok.implements(interfaces.IInvisibleService)
    grok.provides(IIntIds)
    silvaconf.default_service(public=False)
