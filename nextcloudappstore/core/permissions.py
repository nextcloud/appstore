from rest_framework.permissions import BasePermission, SAFE_METHODS


class AllowedToEditApp(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_object_permission(self, request, view, app):
        return (
            request.method in SAFE_METHODS or
            (
                request.user and
                request.user.is_authenticated() and
                app.allows_editing(request.user)
            )
        )
