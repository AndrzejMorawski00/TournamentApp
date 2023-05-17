from django.shortcuts import redirect


def user_not_authenticated(function=None, redirect_url='/'):
    def decorator(view_func):
        def wrapped_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)

        return wrapped_func
    if function:
        return decorator(function)
    return decorator


def user_authenticated(function=None, redirect_url='/'):
    def decorator(view_func):
        def wrapped_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            return redirect(redirect_url)
        return wrapped_func
    if function:
        return decorator(function)
    return decorator


def group_based_access(function=None, redirect_url="/", groups=[]):
    def decorator(view_func):
        def wrapped_func(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return view_func(request, *args, **kwargs)
            return redirect(redirect_url)
        return wrapped_func
    if function:
        return decorator(function)
    return decorator
