from silva.core import interfaces


def walk_silva_tree(content):
    """A generator to lazily get all the objects that need to be
    indexed.
        """
    if interfaces.ISilvaObject.providedBy(content):
        # Version are indexed by the versioned content itself
        yield content
    if interfaces.IContainer.providedBy(content):
        for child in content.objectValues():
            for content in walk_silva_tree(child):
                yield content
