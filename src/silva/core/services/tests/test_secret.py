# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from silva.core.services.interfaces import ISecretService

from Products.Silva.testing import FunctionalLayer


class SecretServiceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_digest(self):
        """Test secret service method: digest.
        """
        service = getUtility(ISecretService)
        self.assertTrue(verifyObject(ISecretService, service))

        key = service.digest('information', 'other', 42)
        # The should stay the same.
        self.assertEqual(
            service.digest('information', 'other', 42),
            key)

        # Unless you generate a new private key.
        service.generate_new_key()
        self.assertNotEqual(
            service.digest('information', 'other', 42),
            key)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecretServiceTestCase))
    return suite
