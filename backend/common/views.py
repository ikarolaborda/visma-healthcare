"""
Views for common models.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ClinicSettings
from .serializers import ClinicSettingsSerializer


class ClinicSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ClinicSettings (singleton).

    Provides endpoints for:
    - Retrieving current clinic settings
    - Updating clinic settings
    - Uploading clinic logo
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ClinicSettingsSerializer
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'put', 'patch']  # No delete or create for singleton

    def get_queryset(self):
        """Return the singleton instance."""
        return ClinicSettings.objects.all()

    def get_object(self):
        """Always return the singleton instance."""
        return ClinicSettings.load()

    def list(self, request, *args, **kwargs):
        """
        Override list to return single object instead of array.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve clinic settings."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update clinic settings."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Partially update clinic settings."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload_logo(self, request):
        """
        Upload clinic logo separately.
        """
        instance = self.get_object()

        if 'logo' not in request.FILES:
            return Response(
                {'error': 'No logo file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.logo = request.FILES['logo']
        instance.save()

        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
