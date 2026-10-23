"""
CustomDRF permission classes enforcing
role-based control (RBAC).
"""
from rest_framework.permissions import BasePermission


class IsEditor(BasePermission):
    """
    Allows access strictly to users with 'editor' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'editor'
        )


class IsJournalist(BasePermission):
    """
    Allows access strictly to users with 'journalist' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'journalist'
        )


class IsJournalistOrEditor(BasePermission):
    """
    Allows access for users with either the 'journalist'
    or 'editor' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in ['journalist', 'editor']
        )


class IsArticleAuthorOrEditor(BasePermission):
    """
    Object-level permission ensuring that only the journalist
    who authored the article (or an editor) can modify or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Editors have global oversight for articles
        if request.user.role == 'editor':
            return True

        # Journalists can only modify their own articles
        if hasattr(obj, 'journalist'):
            return obj.journalist == request.user

        return False
