import csv
from io import TextIOWrapper

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path, reverse

from users_management.models import User
from users_management.validators import StrongPasswordValidator


class CSVUploadForm(forms.Form):
    """
    Form for uploading a CSV file in the admin panel.
    """
    csv_file = forms.FileField(label="Upload CSV File (Emails and Referral Code)")


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    search_fields = ('email', 'first_name', 'last_name', 'user_type')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'user_type', 'is_institute', 'referral_code', 'recommended_by')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'recommended_by')}),
    )

    exclude = ('username',)

    list_display = ('email', 'user_type', 'is_institute', 'is_active')

    ordering = ['email']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Customizing the queryset for the recommended_by field.
        """
        if db_field.name == "recommended_by":
            kwargs["queryset"] = User.objects.filter(is_institute=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def bulk_create_users(self, request):
        """
        Handle bulk creation of users from a CSV file with validations, normalization, and password hashing.
        """
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                try:
                    csv_data = TextIOWrapper(csv_file.file, encoding='utf-8')
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    users_to_create = []
                    error_messages = []

                    password_validator = StrongPasswordValidator()

                    with transaction.atomic():
                        for row in reader:
                            email = row[0].strip()
                            referral_code = row[1].strip() if len(row) > 1 else None
                            password = row[2].strip() if len(row) > 2 else None

                            try:
                                validate_email(email)
                                email = email.lower()
                            except ValidationError:
                                error_messages.append(f"Invalid email format for: {email}")
                                break

                            try:
                                password_validator.validate(password)
                            except ValidationError as e:
                                error_messages.append(f"Password validation failed for email {email}: {str(e)}")
                                break

                            password = make_password(password)

                            recommended_by = None
                            if referral_code:
                                try:
                                    recommended_by = User.objects.get(referral_code=referral_code)
                                except User.DoesNotExist:
                                    error_messages.append(f"Invalid referral code '{referral_code}' for email: {email}")
                                    break

                            if User.objects.filter(email=email).exists():
                                error_messages.append(f"User with email {email} already exists.")
                                break

                            user = User(
                                email=email,
                                password=password,
                                recommended_by=recommended_by
                            )
                            users_to_create.append(user)

                        if not error_messages:
                            if users_to_create:
                                User.objects.bulk_create(users_to_create)
                                messages.success(request, f"{len(users_to_create)} users created successfully.")
                        else:
                            messages.error(request, "Errors occurred: " + " | ".join(error_messages))

                except Exception as e:
                    messages.error(request, f"Error processing CSV file: {str(e)}")

                return redirect(request.path)
        else:
            form = CSVUploadForm()

        return render(request, 'admin/csv_upload_form.html', {'form': form, 'title': 'Bulk Create Users'})


    def changelist_view(self, request, extra_context=None):
        """
        Add the bulk create users button to the changelist page.
        """
        extra_context = extra_context or {}
        extra_context['bulk_create_users_url'] = reverse('admin:bulk_create_users')
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        """
        Add custom URLs for handling the CSV upload.
        """
        urls = super().get_urls()
        custom_urls = [
            path('bulk-create-users/', self.admin_site.admin_view(self.bulk_create_users), name='bulk_create_users'),
        ]
        return custom_urls + urls

admin.site.register(User, CustomUserAdmin)
