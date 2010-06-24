# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import interfaces

THRESHOLD = 1000

def walk_silva_tree(content):
    """A generator to lazily get all the objects that need to be
    indexed.
        """
    if interfaces.ISilvaObject.providedBy(content):
        # Version are indexed by the versioned content itself
        yield content
    count = 0
    if interfaces.IContainer.providedBy(content):
        for child in content.objectValues():
            for content in walk_silva_tree(child):
                count += 1
                yield content
                if count > THRESHOLD:
                    # Review ZODB cache
                    content._p_jar.cacheGC()
