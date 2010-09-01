# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from silva.core.interfaces import ISilvaService, IInvisibleService


class ICatalogingAttributes(Interface):
    """Represent attributes of a content to catalog.
    """

    def __getattr__(name):
        pass


class ICataloging(Interface):
    """Cataloging support for Silva objects.
    """

    def index(indexes=None):
        """Index the content in the catalog. If a list of indexes
        names is given as argument, only those indexes will be indexed.
        """

    def reindex(indexes=None):
        """Re-index a content in the catalog. If a list of indexes
        names is given as argument, only those indexes will re-indexed.
        """

    def unindex():
        """Un-index a content from the catalog.
        """


class ICatalogService(ISilvaService):
    """Catalog Service, used to catalog content.
    """


class IMemberService(ISilvaService):
    """Member service.
    """

    def find_members(search_string, location=None):
        """Return all users with a full name containing search string
        at the given position.
        """

    def is_user(userid, location=None):
        """Return true if userid is indeed a known user within the
        site at the given position.
        """

    def get_member(userid, location=None):
        """Get member object for userid, or None if no such member
        object.
        """

    def get_cached_member(userid, location=None):
        """Get member which can be cached, or None if no such.
        """

    def logout(came_from=None, REQUEST=None):
        """Logout the current user.
        """


class IGroupService(ISilvaService):

    def find_groups(search_string, location=None):
        """Return all users with a full name containing search string
        at the given position.
        """

    def is_group(groupid, location=None):
        """Return true if userid is indeed a known user.
        """

    def get_group(self, groupid, location=None):
        """Return the given group.
        """

    def use_groups(location=None):
        """Return true if groups are in used in this site.
        """


class IContainerPolicyService(ISilvaService, IInvisibleService):

    def get_policy(name):
        """Return the named policy.
        """

    def list_policies():
        """List all available policies.
        """

    def list_addable_policies(container):
        """List all available policies that can be used on the given
        container.
        """

    def register(name, policy, priority=0.0):
        """Register a new policy. Name should content meta_type.
        """

    def unregister(name):
        """Unregister a policy.
        """
