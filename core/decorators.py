from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    """Restrict a view to users whose `role` is one of `roles`."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect("core:post_login_redirect")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
