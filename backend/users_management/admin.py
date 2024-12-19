from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from users_management.models import User


class CustomUserAdmin(UserAdmin):
    # Use the default Django forms
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    # Adjust the fieldsets to match your User model
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'user_type', 'is_institute', 'referral_code', 'recommended_by')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Define the fields for the "add" form (creating a new user)
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'recommended_by')}),
    )

    # Exclude any non-existing fields in your User model
    exclude = ('username',)

    # Adjust list_display to show only available fields
    list_display = ('email', 'user_type', 'is_institute', 'is_active')


    # Ordering by email or any other field present in your model
    ordering = ['email']

    # Customizing the queryset for the recommended_by field
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "recommended_by":
            kwargs["queryset"] = User.objects.filter(is_institute=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(User, CustomUserAdmin)
