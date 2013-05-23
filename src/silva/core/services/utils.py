# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.interfaces import ISilvaObject, IContainer, IVersionedContent

THRESHOLD = 1000

def walk_silva_tree(content, requires=ISilvaObject, version=False):
    """A generator to lazily get all the Silva object from a content /
    container.
    """

    def walker(context):
        if requires.providedBy(context):
            # Version are indexed by the versioned content itself
            yield context
        if IContainer.providedBy(context):
            for child in context.objectValues():
                for context in walker(child):
                    yield context
        elif version and IVersionedContent.providedBy(context):
            yield context.get_previewable()

    count = 0
    for context in walker(content):
        yield context
        count += 1
        if count > THRESHOLD:
            # Review ZODB cache
            content._p_jar.cacheGC()
            count = 0


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
    if want_next:
        if IContainer.providedBy(content):
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
            yield content.get_previewable()

# BBB
advanced_walk_silva_tree = walk_silva_tree_ex
