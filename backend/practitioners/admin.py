"""
Django admin configuration for Practitioner models.
"""

from django.contrib import admin
from .models import Practitioner


@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    """Admin interface for Practitioner model."""

    list_display = [
        'get_credentials',
        'specialization',
        'email',
        'phone',
        'npi',
        'active',
        'created_at',
    ]
    list_filter = ['active', 'specialization', 'gender', 'created_at']
    search_fields = [
        'given_name',
        'family_name',
        'email',
        'npi',
        'specialization',
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'prefix', 'given_name', 'middle_name', 'family_name', 'gender', 'birth_date')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'qualification', 'years_of_experience', 'npi', 'license_number')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address_line', 'address_city', 'address_state', 'address_postal_code', 'address_country')
        }),
        ('Status', {
            'fields': ('active', 'created_at', 'updated_at')
        }),
    )

    def get_credentials(self, obj):
        """Display practitioner credentials in list view."""
        return obj.get_credentials()
    get_credentials.short_description = 'Practitioner'
