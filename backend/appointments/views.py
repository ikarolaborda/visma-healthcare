"""
API Views for Appointment endpoints.

This module provides REST API endpoints for Appointment resources,
including standard CRUD operations and custom actions for appointment workflows.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from uuid import UUID
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Appointment
from .services import AppointmentService
from .serializers import AppointmentSerializer, FHIRAppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Appointment resources.

    Provides endpoints for:
    - CRUD operations on appointments
    - Searching by patient, practitioner, date range, status
    - Workflow actions: book, cancel, check-in, arrive, fulfill, no-show
    - Availability checking
    - Schedule retrieval

    All endpoints require authentication via JWT token.
    Supports both standard Django and FHIR R4 formats via query parameter.
    """

    permission_classes = [IsAuthenticated]
    service = AppointmentService()

    def get_queryset(self):
        """
        Get filtered queryset based on query parameters.

        Supports filtering by:
        - patient_id: Filter by patient UUID
        - practitioner_id: Filter by practitioner UUID
        - status: Filter by appointment status
        - start_date: Filter appointments starting on or after this date
        - end_date: Filter appointments starting on or before this date
        - upcoming: Show only upcoming appointments (boolean)
        """
        queryset = Appointment.objects.all().select_related('patient', 'practitioner')

        # Filter by patient
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        # Filter by practitioner
        practitioner_id = self.request.query_params.get('practitioner_id')
        if practitioner_id:
            queryset = queryset.filter(practitioner_id=practitioner_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(start__gte=start_dt)
            except ValueError:
                pass  # Invalid date format, ignore filter

        end_date = self.request.query_params.get('end_date')
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(start__lte=end_dt)
            except ValueError:
                pass

        # Filter upcoming appointments
        upcoming = self.request.query_params.get('upcoming')
        if upcoming and upcoming.lower() in ['true', '1', 'yes']:
            now = timezone.now()
            queryset = queryset.filter(
                start__gte=now,
                status__in=['proposed', 'pending', 'booked', 'waitlist']
            )

        return queryset.order_by('-start')

    def get_serializer_class(self):
        """
        Return appropriate serializer based on format query parameter.

        - format=standard: Returns AppointmentSerializer (Django format)
        - Default: Returns FHIRAppointmentSerializer (FHIR R4 format)
        """
        format_param = self.request.query_params.get('format', 'fhir')
        if format_param.lower() == 'standard':
            return AppointmentSerializer
        return FHIRAppointmentSerializer

    @swagger_auto_schema(
        operation_description="Create a new appointment",
        request_body=AppointmentSerializer,
        responses={
            201: AppointmentSerializer,
            400: "Validation error"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new appointment with validation.

        Validates:
        - Required fields (patient, practitioner, start, end)
        - Timing constraints (end > start, future appointments)
        - No scheduling conflicts
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Validate business rules
            self.service.validate_create(serializer.validated_data)

            # Create appointment
            appointment = self.service.create(serializer.validated_data)

            # Return response
            output_serializer = self.get_serializer(appointment)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Update an existing appointment",
        request_body=AppointmentSerializer,
        responses={
            200: AppointmentSerializer,
            400: "Validation error",
            404: "Appointment not found"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Update an existing appointment with validation.

        Validates:
        - Timing constraints if times are being changed
        - No scheduling conflicts if practitioner or times change
        - Valid status transitions
        """
        appointment = self.get_object()
        serializer = self.get_serializer(appointment, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        try:
            # Validate business rules
            self.service.validate_update(appointment, serializer.validated_data)

            # Update appointment
            updated_appointment = self.service.update(
                appointment.id,
                serializer.validated_data
            )

            # Return response
            output_serializer = self.get_serializer(updated_appointment)
            return Response(output_serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Partially update an existing appointment",
        request_body=AppointmentSerializer,
        responses={
            200: AppointmentSerializer,
            400: "Validation error",
            404: "Appointment not found"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update with validation."""
        appointment = self.get_object()
        serializer = self.get_serializer(appointment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            # Validate business rules
            self.service.validate_update(appointment, serializer.validated_data)

            # Update appointment
            updated_appointment = self.service.update(
                appointment.id,
                serializer.validated_data
            )

            # Return response
            output_serializer = self.get_serializer(updated_appointment)
            return Response(output_serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Delete an appointment",
        responses={
            204: "Appointment deleted successfully",
            400: "Cannot delete appointment",
            404: "Appointment not found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete an appointment with validation.

        Prevents deletion of:
        - Fulfilled appointments (should be cancelled instead)
        - Past appointments that aren't cancelled or no-show
        """
        appointment = self.get_object()

        try:
            # Validate deletion
            self.service.validate_delete(appointment)

            # Delete appointment
            self.service.delete(appointment.id)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Book a proposed or pending appointment",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={
            200: AppointmentSerializer,
            400: "Cannot book appointment",
            404: "Appointment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        """
        Book a proposed or pending appointment.

        Changes status to 'booked' and sets participant statuses to 'accepted'.
        Re-checks availability before booking.
        """
        try:
            appointment = self.service.book_appointment(UUID(pk))
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Cancel an appointment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'cancellation_reason': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Reason for cancellation'
                )
            }
        ),
        responses={
            200: AppointmentSerializer,
            400: "Cannot cancel appointment",
            404: "Appointment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment.

        Accepts optional cancellation_reason in request body.
        Invalidates practitioner availability cache.
        """
        cancellation_reason = request.data.get('cancellation_reason', '')

        try:
            appointment = self.service.cancel_appointment(
                UUID(pk),
                cancellation_reason=cancellation_reason
            )
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Check in patient for appointment",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={
            200: AppointmentSerializer,
            400: "Cannot check in",
            404: "Appointment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """
        Check in patient for appointment.

        Only allowed for booked appointments within 30 minutes of start time.
        Changes status to 'checked-in'.
        """
        try:
            appointment = self.service.check_in_appointment(UUID(pk))
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mark patient as arrived",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={
            200: AppointmentSerializer,
            400: "Cannot mark as arrived",
            404: "Appointment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def arrive(self, request, pk=None):
        """
        Mark patient as arrived for appointment.

        Only allowed from 'booked' or 'checked-in' statuses.
        Changes status to 'arrived'.
        """
        try:
            appointment = self.service.mark_as_arrived(UUID(pk))
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mark appointment as fulfilled (completed)",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={
            200: AppointmentSerializer,
            400: "Cannot mark as fulfilled",
            404: "Appointment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        """
        Mark appointment as fulfilled (completed).

        Only allowed from 'arrived', 'checked-in', or 'booked' statuses.
        Terminal state - cannot be changed after this.
        """
        try:
            appointment = self.service.mark_as_fulfilled(UUID(pk))
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mark appointment as no-show",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={
            200: AppointmentSerializer,
            400: "Cannot mark as no-show",
            404: "Appointment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def noshow(self, request, pk=None):
        """
        Mark appointment as no-show.

        Only allowed after appointment end time.
        Only from 'booked', 'checked-in', or 'arrived' statuses.
        Terminal state.
        """
        try:
            appointment = self.service.mark_as_noshow(UUID(pk))
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Check practitioner availability for a time slot",
        manual_parameters=[
            openapi.Parameter(
                'practitioner_id',
                openapi.IN_QUERY,
                description="UUID of the practitioner",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'start',
                openapi.IN_QUERY,
                description="Start time (ISO 8601 format)",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'end',
                openapi.IN_QUERY,
                description="End time (ISO 8601 format)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'practitioner_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'start': openapi.Schema(type=openapi.TYPE_STRING),
                    'end': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: "Missing or invalid parameters"
        }
    )
    @action(detail=False, methods=['get'])
    def check_availability(self, request):
        """
        Check if a practitioner is available for a time slot.

        Query parameters:
        - practitioner_id: UUID of the practitioner
        - start: Start time (ISO 8601 format)
        - end: End time (ISO 8601 format)

        Returns availability status with Redis caching.
        """
        practitioner_id = request.query_params.get('practitioner_id')
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')

        if not all([practitioner_id, start_str, end_str]):
            return Response(
                {'error': 'practitioner_id, start, and end parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            practitioner_uuid = UUID(practitioner_id)
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid parameter format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_available = self.service.check_availability(
            practitioner_uuid,
            start,
            end
        )

        return Response({
            'available': is_available,
            'practitioner_id': practitioner_id,
            'start': start_str,
            'end': end_str
        })

    @swagger_auto_schema(
        operation_description="Get upcoming appointments",
        manual_parameters=[
            openapi.Parameter(
                'patient_id',
                openapi.IN_QUERY,
                description="Filter by patient UUID",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'practitioner_id',
                openapi.IN_QUERY,
                description="Filter by practitioner UUID",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'days_ahead',
                openapi.IN_QUERY,
                description="Number of days to look ahead (default 30)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: AppointmentSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming appointments.

        Query parameters:
        - patient_id: Optional patient UUID filter
        - practitioner_id: Optional practitioner UUID filter
        - days_ahead: Number of days to look ahead (default 30)

        Returns appointments with status: proposed, pending, booked, or waitlist.
        """
        patient_id = request.query_params.get('patient_id')
        practitioner_id = request.query_params.get('practitioner_id')
        days_ahead = int(request.query_params.get('days_ahead', 30))

        try:
            patient_uuid = UUID(patient_id) if patient_id else None
            practitioner_uuid = UUID(practitioner_id) if practitioner_id else None
        except ValueError as e:
            return Response(
                {'error': f'Invalid UUID format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointments = self.service.get_upcoming_appointments(
            patient_id=patient_uuid,
            practitioner_id=practitioner_uuid,
            days_ahead=days_ahead
        )

        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get today's appointments",
        manual_parameters=[
            openapi.Parameter(
                'patient_id',
                openapi.IN_QUERY,
                description="Filter by patient UUID",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'practitioner_id',
                openapi.IN_QUERY,
                description="Filter by practitioner UUID",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: AppointmentSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get today's appointments.

        Query parameters:
        - patient_id: Optional patient UUID filter
        - practitioner_id: Optional practitioner UUID filter

        Returns all appointments scheduled for today regardless of status.
        """
        patient_id = request.query_params.get('patient_id')
        practitioner_id = request.query_params.get('practitioner_id')

        try:
            patient_uuid = UUID(patient_id) if patient_id else None
            practitioner_uuid = UUID(practitioner_id) if practitioner_id else None
        except ValueError as e:
            return Response(
                {'error': f'Invalid UUID format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointments = self.service.get_todays_appointments(
            patient_id=patient_uuid,
            practitioner_id=practitioner_uuid
        )

        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
