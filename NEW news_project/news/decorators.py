"""
Custom view decorators for enforcing role-based access control
(RBAC) on web views.
"""

from functools import wraps
from django.shortcuts import redirect


def role_required(allowed_roles):
    """
    Decorator that restricts view access to users
    belonging to specific roles. Redirects unauthorized
    users to the dashboard router.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:  # noqa: E501
                return view_func(request, *args, **kwargs)
            return redirect('dashboard_redirect')
        return _wrapped_view
    return decorator
