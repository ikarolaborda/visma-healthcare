"""
Django admin configuration for Appointment models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for Appointment model."""

    list_display = [
        'id',
        'patient_display',
        'practitioner_display',
        'status_display',
        'start',
        'end',
        'duration_display',
        'service_type',
        'created',
    ]
    list_filter = [
        'status',
        'service_category',
        'service_type',
        'specialty',
        'priority',
        'patient_status',
        'practitioner_status',
        'created',
    ]
    search_fields = [
        'id',
        'patient__given_name',
        'patient__family_name',
        'practitioner__given_name',
        'practitioner__family_name',
        'reason_code',
        'description',
    ]
    readonly_fields = [
        'id',
        'created',
        'updated_at',
        'duration_display',
        'is_upcoming',
        'can_cancel',
        'can_check_in',
    ]
    date_hierarchy = 'start'
    ordering = ['-start']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'status')
        }),
        ('Service Information', {
            'fields': (
                'service_category',
                'service_type',
                'specialty',
                'appointment_type',
                'priority'
            )
        }),
        ('Scheduling', {
            'fields': (
                'start',
                'end',
                'minutes_duration',
                'duration_display'
            )
        }),
        ('Participants', {
            'fields': (
                'patient',
                'patient_status',
                'practitioner',
                'practitioner_status',
                'practitioner_required'
            )
        }),
        ('Details', {
            'fields': (
                'reason_code',
                'reason_description',
                'description',
                'comment',
                'patient_instruction'
            )
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason',),
            'classes': ('collapse',)
        }),
        ('Status Information', {
            'fields': (
                'is_upcoming',
                'can_cancel',
                'can_check_in',
                'created',
                'updated_at'
            )
        }),
    )

    def patient_display(self, obj):
        """Display patient name with link."""
        if obj.patient:
            return format_html(
                '<a href="/admin/patients/patient/{}/change/">{}</a>',
                obj.patient.id,
                obj.patient.get_full_name()
            )
        return '-'
    patient_display.short_description = 'Patient'

    def practitioner_display(self, obj):
        """Display practitioner name with link."""
        if obj.practitioner:
            return format_html(
                '<a href="/admin/practitioners/practitioner/{}/change/">{}</a>',
                obj.practitioner.id,
                obj.practitioner.get_full_name()
            )
        return '-'
    practitioner_display.short_description = 'Practitioner'

    def status_display(self, obj):
        """Display status with color coding."""
        color_map = {
            'proposed': '#6c757d',  # Gray
            'pending': '#ffc107',   # Yellow
            'booked': '#17a2b8',    # Cyan
            'arrived': '#007bff',   # Blue
            'fulfilled': '#28a745', # Green
            'cancelled': '#dc3545', # Red
            'noshow': '#fd7e14',    # Orange
            'entered-in-error': '#6c757d',  # Gray
            'checked-in': '#20c997', # Teal
            'waitlist': '#6f42c1',   # Purple
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def duration_display(self, obj):
        """Display appointment duration in minutes."""
        return f"{obj.get_duration_minutes()} minutes"
    duration_display.short_description = 'Duration'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('patient', 'practitioner')

    actions = ['mark_as_booked', 'mark_as_cancelled', 'mark_as_fulfilled']

    def mark_as_booked(self, request, queryset):
        """Admin action to mark appointments as booked."""
        updated = queryset.filter(
            status__in=['proposed', 'pending']
        ).update(status='booked')
        self.message_user(request, f'{updated} appointments marked as booked.')
    mark_as_booked.short_description = 'Mark selected as booked'

    def mark_as_cancelled(self, request, queryset):
        """Admin action to cancel appointments."""
        updated = queryset.exclude(
            status__in=['cancelled', 'fulfilled', 'noshow', 'entered-in-error']
        ).update(status='cancelled')
        self.message_user(request, f'{updated} appointments cancelled.')
    mark_as_cancelled.short_description = 'Cancel selected appointments'

    def mark_as_fulfilled(self, request, queryset):
        """Admin action to mark appointments as fulfilled."""
        updated = queryset.filter(
            status__in=['arrived', 'checked-in', 'booked']
        ).update(status='fulfilled')
        self.message_user(request, f'{updated} appointments marked as fulfilled.')
    mark_as_fulfilled.short_description = 'Mark selected as fulfilled'
