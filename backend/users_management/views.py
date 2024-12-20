import logging

from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import AnonRateThrottle
from silk.profiling.profiler import silk_profile

from users_management.models import User
from users_management.serializers import UserSerializer

logger = logging.getLogger(__name__)

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
    pagination_class = PageNumberPagination

    def get_permissions(self):
        """
        Assign permissions dynamically based on the action.
        """
        if self.action == 'create':
            self.throttle_classes = [AnonRateThrottle]
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'destroy':
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @silk_profile(name='Get User')
    def get_queryset(self):
        """
        Restrict the queryset to the current user for non-admin users.
        """
        user = self.request.user

        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @silk_profile(name='Update User')
    def perform_update(self, serializer):
        """
        Allow users to update only their own data.
        """
        if self.request.user != self.get_object():
            raise PermissionDenied("You are not allowed to update this user.")
        logger.info(f"User {self.request.user.email} updated their account.")
        serializer.save()

    @silk_profile(name='Delete User')
    def perform_destroy(self, instance):
        """
        Only allow admin users to delete a user.
        """
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this user.")
        logger.warning(f"Admin {self.request.user.email} deleted user {instance.email}.")
        instance.delete()

    @silk_profile(name='Create User')
    def perform_create(self, serializer):
        """
        Create a new user with Silk profiling.
        """
        user = serializer.save()
        logger.info(f"User {user.email} created successfully.")