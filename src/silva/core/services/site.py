# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.intid.interfaces import IIntIds

from silva.core.services.base import IntIdService


class Site(grok.Site):

    grok.local_utility(IntIdService, IIntIds)
