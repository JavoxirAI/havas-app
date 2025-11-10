from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allow admins to create/edit/delete
    Allow everyone to read (GET)
    """

    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS - everyone can access
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # POST, PUT, PATCH, DELETE - only admins
        return request.user and request.user.is_staff