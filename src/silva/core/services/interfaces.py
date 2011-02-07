# Copyright (c) 2009-2011 Infrae. All rights reserved.
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


class MemberLookupError(Exception):
    """Exception raised then a user or group search failed. A
    comprehensive message, possiblity translated would be the first
    argument.
    """


class IMemberService(ISilvaService):
    """Member service, which is able to lookup members.
    """

    def find_members(search_string, location=None):
        """Return all members object corresponding to users which
        theirs fullname contains ``search_string``. Search is done at
        the given ``location`` if provided.

        :raises: :py:exc:`~silva.core.services.interfaces.MemberLookupError`
        :return: a list of :py:class:`~silva.core.interfaces.auth.IMember`
                 objects.
        """

    def is_user(userid, location=None):
        """Return true if ``userid`` is indeed a known user within the
        site at the given ``location`` if provided.

        :return: a boolean.
        """

    def get_member(userid, location=None):
        """Get member object for ``userid``, or None if no such member
        object within the site at the given ``location`` if provided.

        :return: an :py:class:`~silva.core.interfaces.auth.IMember`
                 object or None.
        """

    def get_cached_member(userid, location=None):
        """Get a member object which can be cached of ``userid``, or
        None if no such, searched within the site at the given
        ``location`` if provided.

        :return: an :py:class:`~silva.core.interfaces.auth.IMember`
                 object or None.
        """

    def logout(came_from=None, REQUEST=None):
        """Logout the current user. If ``came_from`` is not None, the
        user will be redirected to this URL. Otherwise he will be
        redirected to the public view of the site's root.
        """


class IGroupService(ISilvaService):
    """Group service can lookup groups.
    """

    def find_groups(search_string, location=None):
        """Return all group objects with a group name containing
        ``search_string``. Search is done from the given ``location``
        if provided.

        :raises: :py:exc:`~silva.core.services.interfaces.MemberLookupError`
        :returns: :py:class: a list of :py:class:`~silva.core.interfaces.auth.IGroup`.
        """

    def is_group(groupid, location=None):
        """Return true if ``groupid`` is indeed a known group at the
        given ``location`` if provided.

        :returns: a boolean.
        """

    def get_group(groupid, location=None):
        """Return the group object corresponding to ``groupid``,
        searched at the given ``location`` if given. Return None if no
        group are found.

        :returns: a :py:class:`~silva.core.interfaces.auth.IGroup`
                  object or None.
        """

    def use_groups(location=None):
        """Return true if groups are in used in this site (at the
        given ``location`` if provided).

        :returns: a boolean.
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


class ISecretService(ISilvaService):

    def generate_new_key():
        """ generate new internal key
        """

    def digest(*args):
        """use args to generate a hmac.
        """
