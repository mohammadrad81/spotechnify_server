from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS, IsAuthenticated


def is_authenticated(request, view):
    """ checks if user is authenticated

    Args:
        request (Request): the request sent by user
        view (View): is the view the user requested to

    Returns:
        bool: True if user is authenticated, else False
    """
    return IsAuthenticated().has_permission(request, view)


def is_admin(request, view):
    """ checks if user is admin

    Args:
        request (Request): the request sent by user
        view (View): is the view the user requested to

    Returns:
        bool: True if user is admin, else False
    """
    return IsAdminUser().has_permission(request, view)