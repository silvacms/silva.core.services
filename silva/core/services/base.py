# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from OFS import SimpleItem
from five import grok

from silva.core import interfaces



class ZMIObject(SimpleItem.SimpleItem):

    grok.baseclass()
    grok.implements(interfaces.IZMIObject)


class SilvaService(ZMIObject):

    grok.baseclass()
    grok.implements(interfaces.ISilvaService)

    def __init__(self, id, title):
        self.id = id
        self.title = title

