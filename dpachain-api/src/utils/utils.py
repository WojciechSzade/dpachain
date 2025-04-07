import functools


def require_authorized(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.authorized:
            raise PermissionError(
                "This operation requires authorized blockchain service")
        return func(self, *args, **kwargs)
    return wrapper
