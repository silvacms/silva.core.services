# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.interfaces import ISilvaObject, IContainer, IVersionedContent

THRESHOLD = 1000

def walk_silva_tree(content, requires=ISilvaObject, version=False):
    """A generator to lazily get all the Silva object from a content /
    container.
    """
    count = 0
    if requires.providedBy(content):
        # Version are indexed by the versioned content itself
        yield content
    if IContainer.providedBy(content):
        for child in content.objectValues():
            for content in walk_silva_tree(child, version=version):
                count += 1
                yield content
                if count > THRESHOLD:
                    # Review ZODB cache
                    content._p_jar.cacheGC()
                    count = 0
    if version and IVersionedContent.providedBy(content):
        yield content.get_previewable()


# XXX need testing.
def walk_silva_tree_ex(content, requires=ISilvaObject, version=False):
    """A controllable generator to lazily get all the Silva object
    from a content / container. Send it True to recursively go down,
    or False to skip the recursion.
    """
    count = 0
    want_next = True
    if requires.providedBy(content):
        want_next = yield content
    if IContainer.providedBy(content) and want_next:
        for child in content.objectValues():
            walker_next = None
            walker = walk_silva_tree_ex(child, requires, version)
            while True:
                count += 1
                try:
                    walker_next = yield walker.send(walker_next)
                except StopIteration:
                    break
                if count > THRESHOLD:
                    # Review ZODB cache
                    content._p_jar.cacheGC()
                    count = 0
    if version and IVersionedContent.providedBy(content):
        want_next = yield content.get_previewable()

# BBB
advanced_walk_silva_tree = walk_silva_tree_ex
