# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from OFS import SimpleItem
from five import grok
from five.intid.intid import OFSIntIds

from silva.core import interfaces



class ZMIObject(SimpleItem.SimpleItem):

    grok.baseclass()
    grok.implements(interfaces.IZMIObject)


class SilvaService(ZMIObject):
    grok.baseclass()
    grok.implements(interfaces.ISilvaService)

    def __init__(self, id, title=None):
        self.id = id
        self.title = title or self.meta_type

    def getId(self):
        if hasattr(self, 'default_service_identifier'):
            return self.default_service_identifier
        return self.id


class IntIdService(OFSIntIds, SilvaService):

    grok.baseclass()
    grok.implements(interfaces.IInvisibleService)
