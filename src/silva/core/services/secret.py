# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
import hmac
import os
import hashlib

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from five import grok
from silva.core import conf as silvaconf
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ISecretService
from zeam.form import silva as silvaforms


class SecretService(SilvaService):
    grok.implements(ISecretService)
    grok.name('service_secret')

    meta_type = 'Silva Secret Service'
    silvaconf.default_service()
    silvaconf.icon('secret.png')

    security = ClassSecurityInfo()
    manage_options = (
        {'label': 'Secret generation service',
         'action': 'manage_main'},) + SilvaService.manage_options

    def __init__(self, id=None):
        super(SecretService, self).__init__(id=id)
        self.generate_new_key()

    security.declareProtected(
        'View management screens', 'generate_new_key')
    def generate_new_key(self):
        self.__key = str(os.urandom(8*8))

    security.declareProtected(
        'Access contents information', 'digest')
    def digest(self, *args):
        assert len(args) > 1, u'Too few arguments'
        challenge = hmac.new(self.__key, str(args[0]), hashlib.sha1)
        for arg in args[1:]:
            challenge.update(str(arg))
        return challenge.hexdigest()

InitializeClass(SecretService)


class SecretServiceView(silvaforms.ZMIForm):
    """Create a new secret.
    """
    grok.name('manage_main')
    grok.context(ISecretService)

    label = u"Generate new key"
    description = u"Generate a new key. Carreful!! secret key is used " \
                  u"in session and authentication management."
    ignoreContent = False
    ignoreRequest = True

    @silvaforms.action(u'Generate new key')
    def generate_new_key(self):
        self.context.generate_new_key()
        self.status = u'Key updated.'
