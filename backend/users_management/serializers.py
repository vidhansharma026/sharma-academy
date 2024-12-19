from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users_management.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    UserRegisterSerializer for the User model. Handles fields for creation and representation.
    """
    confirm_password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    referral_code = serializers.CharField(allow_blank=True, required=False, write_only=True)
    class Meta:
        model = User
        fields = [
            'email', 'password', 'confirm_password', 'referral_code'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Ensure passwords match
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Validate password strength
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({"password": e})

        return data
    
    def create(self, validated_data):
        """
        Create method to handle referral-based registration.
        """
        referral_code = validated_data.pop('referral_code', None)
        recommended_by = None

        if referral_code:
            try:
                recommended_by = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                raise serializers.ValidationError({"referral_code": "Invalid referral code."})

        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password')
        try:
            user = User.objects.create_user(**validated_data, recommended_by=recommended_by)
            return user  
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})
