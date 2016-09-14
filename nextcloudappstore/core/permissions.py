from rest_framework.permissions import BasePermission

DELETE_METHODS = ('DELETE',)
UPDATE_METHODS = ('PUT', 'PATCH', 'POST')
READ_METHODS = ('GET', 'HEAD', 'OPTIONS')


class UpdateDeletePermission(BasePermission):
    """
    Base permission which allows anyone to read the resources but allows
    to set different methods for updating and deleting resources for
    authenticated users
    """

    def has_update_obj_permission(self, user, obj):
        return obj.can_update(user)

    def has_delete_obj_permission(self, user, obj):
        return obj.can_delete(user)

    def has_object_permission(self, request, view, obj):
        method = request.method

        if method in READ_METHODS:
            return True
        elif request.user and request.user.is_authenticated:
            user = request.user
            if method in UPDATE_METHODS:
                return self.has_update_obj_permission(user, obj)
            elif method in DELETE_METHODS:
                return self.has_delete_obj_permission(user, obj)
        return False
