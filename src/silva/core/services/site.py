# Copyright (c) 2009-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.intid.interfaces import IIntIds
from zope.container.interfaces import IContainer

from silva.core.services import interfaces
from silva.core.services.base import IntIdService
from silva.core.services.secret import SecretService


class Site(grok.Site):
    grok.implements(IContainer)
    grok.local_utility(IntIdService, IIntIds)
    grok.local_utility(SecretService, interfaces.ISecretService,
                       public=True, name_in_container='service_secret')
