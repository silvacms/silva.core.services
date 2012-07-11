
import unittest

from Products.Silva.testing import FunctionalLayer


class UtilsTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_walk(self):
        assert False, 'TBD'

    def test_walk_advanced(self):
        assert False, 'TBD'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilsTestCase))
    return suite
