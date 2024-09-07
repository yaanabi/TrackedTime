from rest_framework import permissions 


class IsOwnerOrRestricted(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff or request.method in ["OPTIONS", "HEAD"]