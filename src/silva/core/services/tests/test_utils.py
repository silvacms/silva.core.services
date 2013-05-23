# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IContainer, IContent, IVersion
from silva.core.services.utils import walk_silva_tree, walk_silva_tree_ex


class EmptyUtilsTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_walk_empty(self):
        """Test walk_silva_tree on an empty tree.
        """
        self.assertEqual(
            list(walk_silva_tree(self.root)),
            [self.root])
        self.assertEqual(
            list(walk_silva_tree(self.root, requires=IContainer)),
            [self.root])
        self.assertEqual(
            list(walk_silva_tree(self.root, requires=IContent)),
            [])
        self.assertEqual(
            list(walk_silva_tree(self.root, requires=IContent, version=True)),
            [])


def consume(parent, stop=[]):
    """Test function to test silva_walk_ex. The object should collect
    found in a list, prevent the exploration of containers contained
    in the stop list.
    """
    received = []
    following = None
    while True:
        try:
            content = parent.send(following)
        except StopIteration:
            break
        received.append(content)
        following = content not in stop
    return received


class UtilsTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')
        factory.manage_addMockupVersionedContent('information', 'Information')
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addAutoTOC('toc', 'TOC')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addMockupVersionedContent('contact', 'Contact')
        factory.manage_addMockupVersionedContent('location', 'Location')

    def test_walk(self):
        """Test walk_silva_tree with some interfaces.
        """
        self.assertEqual(
            list(walk_silva_tree(self.root)),
            [self.root,
             self.root.folder,
             self.root.publication,
             self.root.publication.toc,
             self.root.publication.folder,
             self.root.publication.contact,
             self.root.publication.location,
             self.root.information])
        self.assertEqual(
            list(walk_silva_tree(self.root, requires=IContainer)),
            [self.root,
             self.root.folder,
             self.root.publication,
             self.root.publication.folder])
        self.assertEqual(
            list(walk_silva_tree(self.root, requires=IContent)),
            [self.root.publication.toc,
             self.root.publication.contact,
             self.root.publication.location,
             self.root.information])
        self.assertEqual(
            list(walk_silva_tree(self.root, requires=IContent, version=True)),
            [self.root.publication.toc,
             self.root.publication.contact,
             self.root.publication.contact.get_editable(),
             self.root.publication.location,
             self.root.publication.location.get_editable(),
             self.root.information,
             self.root.information.get_editable()])
        self.assertEqual(
            list(walk_silva_tree(self.root, requires=IVersion, version=True)),
            [self.root.publication.contact.get_editable(),
             self.root.publication.location.get_editable(),
             self.root.information.get_editable()])

    def test_walk_advanced(self):
        """Test walk_silva_tree_ex with some interfaces and stop list.
        """
        self.assertEqual(
            consume(walk_silva_tree_ex(self.root)),
            [self.root,
             self.root.folder,
             self.root.publication,
             self.root.publication.toc,
             self.root.publication.folder,
             self.root.publication.contact,
             self.root.publication.location,
             self.root.information])
        self.assertEqual(
            consume(walk_silva_tree_ex(self.root, IContainer)),
            [self.root,
             self.root.folder,
             self.root.publication,
             self.root.publication.folder])
        self.assertEqual(
            consume(walk_silva_tree_ex(self.root),
                    [self.root.publication]),
            [self.root,
             self.root.folder,
             self.root.publication,
             self.root.information])
        self.assertEqual(
            consume(walk_silva_tree_ex(self.root, IContainer),
                    [self.root.publication]),
            [self.root,
             self.root.folder,
             self.root.publication])
        self.assertEqual(
            consume(walk_silva_tree_ex(self.root, IContent, version=True)),
            [self.root.publication.toc,
             self.root.publication.contact,
             self.root.publication.contact.get_editable(),
             self.root.publication.location,
             self.root.publication.location.get_editable(),
             self.root.information,
             self.root.information.get_editable()])
        # This case is confusing. The stop object doesn't implement
        # the given iface, so it is not yield, and don't receive any
        # order to block the recursion in the stop object.
        self.assertEqual(
            consume(walk_silva_tree_ex(self.root, IContent, version=True),
                    [self.root.publication]),
            [self.root.publication.toc,
             self.root.publication.contact,
             self.root.publication.contact.get_editable(),
             self.root.publication.location,
             self.root.publication.location.get_editable(),
             self.root.information,
             self.root.information.get_editable()])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EmptyUtilsTestCase))
    suite.addTest(unittest.makeSuite(UtilsTestCase))
    return suite
