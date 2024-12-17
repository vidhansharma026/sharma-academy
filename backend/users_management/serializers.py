from rest_framework import serializers
from users_management.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model. Handles fields for creation and representation.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'user_type', 'is_institute',
            'referral_code', 'recommended_by', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'referral_code', 'recommended_by', 'date_joined', 'last_login']

    def create(self, validated_data):
        """
        Create method to handle referral-based registration.
        """
        referral_code = validated_data.pop('referral_code', None)
        recommended_by = None

        # Find the user who owns the referral code
        if referral_code:
            try:
                recommended_by = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                raise serializers.ValidationError({"referral_code": "Invalid referral code."})

        # Create the user instance
        user = User.objects.create(**validated_data, recommended_by=recommended_by)
        return user
