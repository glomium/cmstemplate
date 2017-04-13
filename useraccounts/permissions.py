#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from rest_framework import permissions


class EmailPermissions(permissions.IsAuthenticated):
    """
    Permissions for User API access.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # update email address to primary
        # only allowed on non-primary and valid addresses
        if request.method in ['PUT', 'PATCH']:
            return not obj.is_primary and obj.is_valid

        # delete email address
        # only allowed, when the email is not primary
        if request.method in ['DELETE']:
            return not obj.is_primary

        return True
