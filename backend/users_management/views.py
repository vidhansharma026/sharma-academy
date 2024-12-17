from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from users_management.models import User
from users_management.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    User API:
    - Any user can create (register).
    - Retrieve: Only current user.
    - Update: Only current user.
    - Delete: Admin users only.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Assign permissions dynamically based on the action.
        """
        if self.action == 'create':
            self.permission_classes = [permissions.AllowAny]  # Registration is open to all
        elif self.action == 'destroy':
            self.permission_classes = [permissions.IsAdminUser]  # Only admin can delete
        else:  # retrieve, update, partial_update
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Restrict the queryset to the current user for non-admin users.
        """
        user = self.request.user

        # Admin can access all users, others can only see their own data
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def perform_update(self, serializer):
        """
        Allow users to update only their own data.
        """
        if self.request.user != self.get_object():
            raise PermissionDenied("You are not allowed to update this user.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Only allow admin users to delete a user.
        """
        if not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to delete this user.")
        instance.delete()