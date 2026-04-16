from django.contrib.auth.models import Group
from ninja.errors import HttpError
from functools import wraps

def is_role(role_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(name=role_name).exists() and not request.user.is_superuser:
                raise HttpError(403, f"Only {role_name} can perform this action.")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def is_instructor(func):
    return is_role("instructor")(func)

def is_admin(func):
    return is_role("admin")(func)

def is_student(func):
    return is_role("student")(func)
