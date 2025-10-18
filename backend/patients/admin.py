"""
Django admin configuration for Patient model.
"""
from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for Patient model."""

    list_display = (
        'id',
        'family_name',
        'given_name',
        'gender',
        'birth_date',
        'email',
        'active',
        'created_at'
    )
    list_filter = ('gender', 'active', 'created_at')
    search_fields = ('family_name', 'given_name', 'email', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'active')
        }),
        ('Name', {
            'fields': ('given_name', 'middle_name', 'family_name')
        }),
        ('Demographics', {
            'fields': ('gender', 'birth_date')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Address', {
            'fields': (
                'address_line',
                'address_city',
                'address_state',
                'address_postal_code',
                'address_country'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
